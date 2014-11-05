#!/usr/bin/env python

from optparse import OptionParser
import csv
import subprocess

class DataSet(object):
    '''A dataset is a class that contains the data and configuration for a
    single line in a graph.'''

    color = None
    title = None
    xvalues = []
    yvalues = []

    def __init__(self, xval, yval):
        self.xvalues = xval
        self.yvalues = yval

    def xmax(self):
        return max(self.xvalues)

    def ymax(self):
        return max(self.yvalues)

    def make_title(self):
        if not self.title:
            return "notitle"
        return "title %s" % repr(self.title)

    def average(self, func):
        bins = dict()
        for x, y in zip(self.xvalues, self.yvalues):
            bins.setdefault(x, []).append(y)
        data = [(x, func(y)) for (x, y) in bins.iteritems()]
        data.sort()
        self.xvalues, self.yvalues = zip(*data)

    def baseline(self, dataset):
        assert self.xvalues == dataset.xvalues
        self.yvalues = [sy / float(by)
            for sy, by in zip(self.yvalues, dataset.yvalues)]

    def clone(self):
        new = DataSet(list(self.xvalues), list(self.yvalues))
        new.color = self.color
        new.title = self.title
        return new

class DataTable(object):
    '''A collection of datasets that allows some rudimentary database
    operations, like select or join.'''

    def __init__(self, datasets):
        self.data = datasets
        assert len(self.data) > 0
        length = len(self.data[0].yvalues)
        for d in self.data:
            assert len(d.yvalues) == length

    def select(self, acceptor):
        cols = [d.yvalues for d in self.data]
        cols.append(self.data[0].xvalues)
        newcols = zip(*[row for row in zip(*cols) if acceptor(row)])
        xvals = newcols.pop()
        return DataTable([DataSet(xvals, col) for col in newcols])

    def __getitem__(self, index):
        return self.data[index]

def build_dataset(csvfd, xcol, ycols=None):
    parse = float
    reader = csv.reader(csvfd)
    header = next(reader)
    columndata = [[] for col in header]
    for row in reader:
        map(lambda d: d[0].append(parse(d[1])), zip(columndata, row))
    if ycols is None:
        ycols = range(len(columndata))
    return [DataSet(columndata[xcol], columndata[ycol]) for ycol in ycols]

def choose_default_color(index):
    # These colors are taken from Cynthia Brewer's ColorBrewer application,
    # specifically the "Set1" qualitative color scheme. Some of the colors are
    # slightly reordered--I moved orange before purple, and I removed yellow.
    # The later colors in the palette fail to show up well in the graph as thin
    # lines and hence are completely removed, although if you want more than six
    # lines on the same graph, you're doing something wrong.
    colors = ["#e41a1c", "#377eb8", "#4daf4a", "#ff7f00",
        "#984ea3", "#a65628"]
    return colors[index]

def make_plot(datasets, outfd):
    basex = datasets[0].xvalues
    for ds in datasets:
        if basex != ds.xvalues:
            raise Exception('Incompatible datasets')
    plot = subprocess.Popen('gnuplot', stdin=subprocess.PIPE, stdout=outfd)
    plot.stdin.write('set term png enhanced\n')
    plot.stdin.write("set datafile separator ','\n")
    plot.stdin.write(plot_commands)
    plot.stdin.write("plot")
    files = []
    for ds in datasets:
        if len(files) > 0:
            plot.stdin.write(',')
        plot.stdin.write(" '-'")

        # Add data columns
        files.append([ds.xvalues, ds.yvalues])

        # With the dataset type
        plot.stdin.write(" with linespoints")

        # Colors
        color = ds.color or choose_default_color(len(files) - 1)
        plot.stdin.write(" linetype rgb \"" + color + "\"")

        # Title
        plot.stdin.write(" " + ds.make_title())
    plot.stdin.write('\n')
    for cols in files:
        for row in zip(*cols):
            plot.stdin.write(','.join(str(col) for col in row) + '\n')
        plot.stdin.write('e\n')
    plot.stdin.close()
    plot.wait()

def main():
    global gImageFile
    parser = OptionParser()
    parser.add_option('-o', '--output', dest='outfile', default='/dev/stdout',
        help="Choose the output file to save the image as")
    (options, args) = parser.parse_args()

    gImageFile = options.outfile

    if len(args) != 1:
        parser.error("Need exactly one file to read")
    with open(args[0], 'rt') as fd:
        exec_file(fd.read(), args[0])

def exec_file(source, path):
    code = compile(source, path, 'exec')
    exec(code)

# The following are the commands that we can use from the graph rules file input
# on the command line.
plot_commands = ''
def add_gnuplot_commands(commands):
    global plot_commands
    if plot_commands:
        plot_commands += '\n'
    plot_commands += commands

def read_csv(filename, xcol):
    with open(filename, 'r') as fd:
        return DataTable(build_dataset(fd, xcol))

gImageFile = None
def plot(datasets):
    with open(gImageFile, 'w') as fd:
        make_plot(datasets, fd)

if __name__ == '__main__':
    main()
