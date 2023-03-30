#!/usr/bin/env perl

=head1
    Create the architecture scheme in svg
    with make_archi.pl --pydep --transform --convert

=head1 REQUIREMENTS
    perl
    python <- pydeps

=cut


use v5.26;
use File::Basename qw/dirname/;
use Getopt::Long qw/GetOptions/;
use File::Slurp qw/read_file write_file/;

my $fp1 = '/tmp/static_archi_generated_1.dot';
my $fp2 = '/tmp/static_archi_generated_2.dot';
my $fp3 = '/tmp/static_archi.svg';
my $fp4 = "/home/mtourneb/Software/Python/Abism/abism/doc/static_archi.svg";
my $in; my $do_pydep; my $do_transform; my $do_convert;
my @last_node;


my %file_doc = (
'util' => {doc => 'Abism utility functions',tip => '',url => 'https://github.com/tinmarino/abism/tree/master/abism/util.py',},
'run' => {doc => 'Run abism code: synchronous or asynchronous',tip => 'functions: run_sync, run_async',url => 'https://github.com/tinmarino/abism/tree/master/abism/run.py',},
'__main__' => {doc => '',tip => '',url => 'https://github.com/tinmarino/abism/tree/master/abism/__main__.py',},
'answer' => {doc => 'List of AnswerSky',tip => '',url => 'https://github.com/tinmarino/abism/tree/master/abism/answer.py',},
'__init__' => {doc => '',tip => '',url => 'https://github.com/tinmarino/abism/tree/master/abism/__init__.py',},
'gtk_window_open' => {doc => 'File dialog opener\nWhen press Ctrl-o',tip => 'for my Ubuntu 19.10 / Gnome 3\n\nRequires GTK, so will usually fail\nBut the tk ask open file is so ugly, and FileOpen may come too',url => 'https://github.com/tinmarino/abism/tree/master/abism/plugin/gtk_window_open.py',},
'profile_line' => {doc => 'Intensity profile drawer\nalong a user defined line',tip => 'Profile line user shower, callback of a tool',url => 'https://github.com/tinmarino/abism/tree/master/abism/plugin/profile_line.py',},
'__init__' => {doc => '',tip => '',url => 'https://github.com/tinmarino/abism/tree/master/abism/plugin/__init__.py',},
'histogram' => {doc => 'Intensity histogram drawer',tip => 'This is drawing the histogram of pixel values. It may be usefull.\nProgrammers, We can implement a selection of the scale cut of the image\nwith a dragging the vertical lines., with a binning of the image,\nthis could even be in real time.',url => 'https://github.com/tinmarino/abism/tree/master/abism/plugin/histogram.py',},
'stat_rectangle' => {doc => 'Statistic rectangle widget callback',tip => 'Get statistics from a user defined rectangle.\nShow them in the standard AnswerFrame',url => 'https://github.com/tinmarino/abism/tree/master/abism/plugin/stat_rectangle.py',},
'window_debug' => {doc => 'Embedded console to evaluate\npython code in Abism context',tip => 'For developers now (maybe one day embed jupyter kernel in main window)',url => 'https://github.com/tinmarino/abism/tree/master/abism/plugin/window_debug.py',},
'window_text' => {doc => 'Helper to open a\nmarkdown text tk window',tip => 'Used by manual and header.\nPress C-? to see the magic.',url => 'https://github.com/tinmarino/abism/tree/master/abism/plugin/window_text.py',},
'window_xterm' => {doc => 'Spawn a xterm python client\nin Abism context',tip => 'Create:\n    1. Jupyter kernel <- in current state\n    2. Xterm console <- in new tk window\n    3. Jupyter client <- in xterm\n\nXterm arguments:\n    -l  log\n    -lc unicode\n    -lf +file descriptor: to log to file\n    -sb scrollback ability on\n    -c  +command: send command (just spawn, no exec like -e)',url => 'https://github.com/tinmarino/abism/tree/master/abism/plugin/window_xterm.py',},
'config' => {doc => '',tip => '',url => 'https://github.com/tinmarino/abism/tree/master/abism/plugin/.ropeproject/config.py',},
'fit_helper' => {doc => 'Leastsquare fit interface',tip => 'Helpers to make a 2D function (i.e Gaussian) fit an array\n\nIDEA: fit Y = F(X,A) where A is a dictionary describing the\nparameters of the function.\n\nNote that the items in the dictionary should all be scalar!\n\nExported: least_sq_fit used in strehl_fit.py',url => 'https://github.com/tinmarino/abism/tree/master/abism/back/fit_helper.py',},
'image_info' => {doc => 'Some array statistical utilities',tip => 'The class you always dreamt of ... is in your dreams',url => 'https://github.com/tinmarino/abism/tree/master/abism/back/image_info.py',},
'strehl_fit' => {doc => 'Advanced classes for leastsq fit.\nOriented for Strehl retrieval\nWith TightBinaryPsf',tip => 'Build fitted parameters from user variables',url => 'https://github.com/tinmarino/abism/tree/master/abism/back/strehl_fit.py',},
'image_function' => {doc => 'Array utilities\nWith PixelMax, get_radial_line',tip => 'works on array to separe matematics and graphics',url => 'https://github.com/tinmarino/abism/tree/master/abism/back/image_function.py',},
'__init__' => {doc => '',tip => '',url => 'https://github.com/tinmarino/abism/tree/master/abism/back/__init__.py',},
'fit_template_function' => {doc => 'Basic fit target functions.\nWith Gaussian2D',tip => 'Also includes a fit_function factory taking an enum as input',url => 'https://github.com/tinmarino/abism/tree/master/abism/back/fit_template_function.py',},
'leastsqbound' => {doc => 'Scipy fit interface.\nFor constrained multivariate\nleast-squares optimization',tip => 'Bounded minimization of the sum of squares of a set of equations.\nSee function leastsqbound, the only one exported.\n\nReferences\n----------\n* F. James and M. Winkler. MINUIT User\'s Guide, July 16, 2004.',url => 'https://github.com/tinmarino/abism/tree/master/abism/back/leastsqbound.py',},
'strehl' => {doc => 'Strehl meter main orchestrator',tip => 'On user demand, perform arithmetic operations:\n1. Read user input\n2. Find first guess parameters\n3. Make a fit\n4. Do some arithmetic\n5. Report the result to user\n\nNote: Error goes along with measure (always)\n\nTODO: prettify, the function division is not judicious:',url => 'https://github.com/tinmarino/abism/tree/master/abism/back/strehl.py',},
'read_header' => {doc => 'Header parser for fits image',tip => 'Necessary:\n    diameter        (real in m)     The primary diameter\n    wavelength      (real in um)    The wavelength of the detection\n    obstruction     (real in %)     The percentage in area of the central\n                                    obstruction. This is 14%**2 for VLT i guess,\n    pixel_scale     (real in arsec/pixel) The number anguler size of one p\n                                    pixel in arcsec\n\nUtil for real intensity/position:\n    exptime         (real in sec)   The time of one exposure.  This will not\n                                    infer the strehl ratio but the potometry\n                                    as well as the zero point.\n    zpt             (real in log)   The luminosity of 1 intensity Arbitrary\n                                    Unit during one second.\n                                    The higher the Zero point, the fainter stars\n                                    (or noise) you may detect.\n                                    It depends on the filter AND the airmass.\n    wcs             (wcs object)    This set of matrices can be used to get the\n                                    position on sky of your object.\n\nHelper:\n    telescope       (string)        Name of your telescope\n    date            (string)        Date, maybe of last modification\n    date_obs        (string)        Data of observation.\n    instrument      (string)        Name of the instrument.\n    company         (string)        Name of the company owning the telescope:\n                                    ESO, CFHT, Carnergie...\n\n    instrument      (string)        Name of the camera. Can be used to\n                                    automatically retrieve information.\n    reduced_type    (string)        RAW or REDUCED\n\n    saturation_level  (real ADU)    The ADU of saturation of the CCD, proper to\n                                    the science camera.  non_lineratiry_level\n                                    (real ADU) The ADU where non linearity starts,\n                                    I wont use this value I guess.\n                                    Or just as a quiet warning.',url => 'https://github.com/tinmarino/abism/tree/master/abism/back/read_header.py',},
'window_root' => {doc => 'Abism GUI main ',tip => '* Create the main tkinter window\n  1. Top menu\n  2. Left text\n  3: Right plot\n* Set the fits image if from command line',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/window_root.py',},
'artist' => {doc => 'Collection of matplotlib artists.\nFor drawing on the plots.\nWith ellipse, annulus, square.',tip => 'ABISM artist collection for drawing figures in matplotlib\nClasses ar Cicle Annulus, Square, etc and they inherit from my custom Artist\n\nNote that all x,y are given for an array, in the image display, x and y must be switched\nIDEA: refactor: mutualize more code',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/artist.py',},
'frame_plot' => {doc => 'The Tkinter right Frame for plotting\nWith Matplotlib',tip => 'RightFrame is the exported class\nIt is vertically divided:\n  * Top: PlotFrame\n  * BottomLeft: 1D view\n  * BottomRight: 2D view',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/frame_plot.py',},
'matplotlib_extension' => {doc => 'Add matplotlib user friendly features\nWith zoom, pane, drag',tip => 'Draggable\nthis module is imported from this web site :\nhttp://www.ster.kuleuven.be/~pieterd/python/html/plotting/interactive_colorbar.html\nit aims to create a colorbar with some events and connecxions,\nif you have some troubles to digest that, just take some laxative\n\nNormalize\n# The Normalize class is largely based on code provided by Sarah Graves.\nif you want to add a scaling fct, like arctan, you need to add it in \"call\" and in \"inverse\"\n\nShould remove abism sutff and git to it as params',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/matplotlib_extension.py',},
'tk_extension' => {doc => 'Monkeypath tkinter\nWith skin and widget alias',tip => 'Extend and MonkeyPatch some tk class and method for:\n1. Skin\n2. Aliases functionality like inserting an abism answer in a text widget\nShould be imported soon enough\n\nThis is faster as moving all to MyTkinter, but if you prefer the latter, you can have a look at:\nlink: https://github.com/fgirault/tkcode <- tkcode a ttk text editor (pretty)',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/tk_extension.py',},
'util_front' => {doc => 'Utility function for Abism GUI',tip => '',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/util_front.py',},
'menu_bar' => {doc => 'Create Menu bar',tip => 'Using MenuBarMaker Factory function to get things as declarative as possible\nJust a binding between buttons and callback.\nSome internal callbacks are changing the button content.\nEach button should have an associated keymap showed in tooltip (like Ctrl-o)',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/menu_bar.py',},
'__init__' => {doc => '',tip => '',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/__init__.py',},
'frame_text' => {doc => 'The Tkinter left frame for text\nWith TextEntry, Label, Buttons',tip => 'LeftFrame is the expoorted class\nThere are some other internal classes separated with a sash\nSo that we get openable, slidy panes',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/frame_text.py',},
'pick' => {doc => 'Pick star action and its callback to science',tip => 'Some class hierarchy, representing the pick type,\nselected by the user in the menu',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/pick.py',},
'answer_return' => {doc => 'To pretty print the answer, may go to FrameText',tip => 'C\'est le bordel !',url => 'https://github.com/tinmarino/abism/tree/master/abism/front/answer_return.py',},
);


sub usage{
    "Usage: $0 [--pydep] [--transform] [--convert]\n";
}

# Create dot
sub pydep{
    system <<EOF;
pydeps  ${\dirname($0)}/../abism --rmprefix abism.front. abism.back. abism.plugin. abism. --exclude-exact abism.front abism.back abism.plugin --show-dot --reverse  --max-bacon=1 --cluster --noshow > $fp1
EOF
}


# Transform dot
sub transform {
    # Read
    $in = read_file $fp1;

    # Remove head
    $in =~ s/^[\s\S]*node \[.*\];\n*//;

    # Remove util
    $in =~ s/^.*\babism_(front_|back_)?(util|answer).*$//gm;

    # Replace main
    $in =~ s/^.*\babism___main__\s*\[.*$/node_main()/gme;
    $in =~ s/^.*\babism_run\s*\[.*$/node_run()/gme;

    # Remove links from plugins
    $in =~ s/^.*abism_plugin.*->.*\n//gm;

    foreach my $k (keys %file_doc) {
        say "found key $k";

        my $doc = $file_doc{$k}{doc};
        my $url = $file_doc{$k}{url};
        my $tip = $file_doc{$k}{tip};

        $doc =~ s/\\n/<br\/>/g;

        my $label = "label=<";
        $label .= "<FONT POINT-SIZE=\"20\">$k</FONT>";
        $label .= "<BR/>";
        $label .= "<FONT POINT-SIZE=\"10\">$doc</FONT>";
        $label .= "<BR/>";
        $label .= ">";

        $label .= ",href=\"$url\"";

        $label .= ",tooltip=\"$tip\"";

        $in =~ s/label="$k"/$label/gme;
    }

    # Remove empty lines
    $in =~ s/^\s*\n//gm;

    # Create output
    my $out = header();
    $out .= front_cluster();
    $out .= back_cluster();
    $out .= plugin_cluster();
    $out .= trick();
    # Prettify plugin cluster (not same rank)
    $out .= '    ' . join(' -> ', @last_node) . " [style=invis];\n";
    $out .= $in;

    # Write
    write_file $fp2, $out;
}


# Convert to png
sub convert {
    system <<EOF,
dot -Tsvg $fp2 > $fp3 && cp $fp3 $fp4 && firefox $fp4
EOF
}


sub nodes {
    my $name = shift;
    my $repl = shift // {};
    my @res = ();
    @last_node = ();
    
    while ($in =~ s/(^\s*($name\w*) \[.*\n)//m){
        my $line = $1;
        for my $key (keys %{$repl}){
            $line =~ s/$key="[^"]*"/$key="$repl->{$key}"/g
        }
        push @res, $line;
        push @last_node, $2;
    }
    my $res = join "\n", @res;
    # Remove empty lines
    $res =~ s/^\s*\n//gms;
    return $res;
}

sub trick { <<EOF;
    // This is to align Front and back
    tin_invis1 [style=invis, label=""];
    abism_front_tk_extension -> abism_front_artist -> tin_invis1 -> abism_back_strehl  [weight=10, style=invis]
EOF
}

# Header
sub header { <<EOF;
digraph G {
    concentrate = true;
    fontsize = 40;
    splines = ortho;
    compound = true;
    label = "ABISM\nAdaptative Background Interactive Strehl Meter";
    labelloc = top;
    // href = "https://github.com/tinmarino/abism";

    node [
      style = filled,
      fillcolor = "#ffffff",
      fontcolor = "#000000",
      fontname = Helvetica,
      fontsize = 15,
      rank = "min",
    ];
    edge [
      overlap=true,
      color="#000000",
    ];
    {
      rank = same;
      abism___main__ ->  abism_run;
    }
EOF
}

# Front
sub front_cluster { "\n\n" . <<EOF;
subgraph cluster_front {
  label = "FrontEnd";
  fontsize = 30;
  fontcolor = "#520C04";
  color = "#520C04";
  penwidth = 5;

${\nodes('abism_front', {
    'fillcolor' => '#D48A7D',
    'fontcolor' => '#000000'
})}
}
EOF
}

# Back
sub back_cluster { "\n\n" . <<EOF;
subgraph cluster_back {
  label = "BackEnd";
  fontsize = 30;
  fontcolor="#003B46";
  color="#003B46";
  penwidth=5;
  rank="min";

${\nodes('abism_back', {
    'fillcolor' => '#BF9EDE',
    'fontcolor' => '#000000'
})}
}
EOF
}

# Plugin
sub plugin_cluster{ "\n\n" . <<EOF;
subgraph cluster_plugin {
  label = "Plugin";
  fontsize = 30;
  fontcolor="#34075E";
  color="#34075E";
  penwidth=5;
  rank="min";
  
${\nodes('abism_plugin', {
    'fillcolor' => '#7FB6C7',
    'fontcolor' => '#000000'
})}
}
EOF
}

# Main
sub node_main { <<'EOF';
    abism___main__ [label="ABISM\nsh> abism\lsh> python path/to/clone/abism.py\lsh> python -m abism\lpy> from abism import __main__\l",
        shape=box, fillcolor="#ffffff",fontcolor="#000000"];
EOF
}


# Run
sub node_run { <<'EOF';
    abism_run [label="run\npy>from abism.run import run_sync; run_sync()\lipy>from abism.run import run_async; sm = run_async()\l",
        shape=box, fillcolor="#ffffff",fontcolor="#000000"];
EOF
}


GetOptions(
    'pydep' => \$do_pydep,
    'transform' => \$do_transform,
    'convert' => \$do_convert
    ) or die usage();

pydep() if $do_pydep;
transform() if $do_transform;
convert() if $do_convert;
