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
my $in; my $do_pydep; my $do_transform; my $do_convert;
my @last_node;


my %file_doc = (
util => 'Abism utility functions',
run => 'Run abism code: synchronous or asynchronous',
__main__ => '',
answer => 'List of AnswerSky',
__init__ => '',
gtk_window_open => 'File dialog opener\nWhen press Ctrl-o',
profile_line => 'Intensity profile drawer\nalong a user defined line',
__init__ => '',
histogram => 'Intensity histogram drawer',
stat_rectangle => 'Statistic rectangle widget callback',
window_debug => 'Embedded console to evaluate\npython code in Abism context',
window_text => 'Helper to open a\nmarkdown text tk window',
window_xterm => 'Spawn a xterm python client\nin Abism context',
config => '',
fit_helper => 'Leastsquare fit interface',
image_info => 'Some array statistical utilities',
strehl_fit => 'Advanced classes for leastsq fit.\nOriented for Strehl retrieval\nWith TightBinaryPsf',
image_function => 'Array utilities\nWith PixelMax, get_radial_line',
__init__ => '',
fit_template_function => 'Basic fit target functions.\nWith Gaussian2D',
leastsqbound => 'Scipy fit interface.\nFor constrained multivariate\nleast-squares optimization',
strehl => 'Strehl meter main orchestrator',
read_header => 'Header parser for fits image',
window_root => 'Abism GUI main ',
artist => 'Collection of matplotlib artists.\nFor drawing on the plots.\nWith ellipse, annulus, square.',
frame_plot => 'The Tkinter Frame for drawings\nAt the right side.\nWith Matplotlib',
matplotlib_extension => 'Add matplotlib user friendly features\nWith zoom, pane, drag',
tk_extension => 'Monkeypath tkinter\nWith skin and widget alias',
util_front => 'Utility function for Abism GUI',
menu_bar => 'Create Menu bar',
__init__ => '',
frame_text => 'The Tkinter Frame for text\nAt the left side.\nWith TextEntry, Label, Buttons',
pick => 'Pick star action and its callback to science',
answer_return => 'To pretty print the answer, may go to FrameText',
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

    while ( my ($k, $v) = each %file_doc ) {
        print "found key $k\n";

        $v =~ s/\\n/<br\/>/g;

        my $label = "label=<";
        $label .= "<FONT POINT-SIZE=\"20\">$k</FONT>";
        $label .= "<BR/>";
        $label .= "<FONT POINT-SIZE=\"10\">$v</FONT>";
        $label .= "<BR/>";
        $label .= ">";

        $in =~ s/label="$k"/$label/gme;
    }

    # Remove empty lines
    $in =~ s/^\s*\n//gm;

    # Create output
    my $out = header();
    $out .= front_cluster();
    $out .= back_cluster();
    $out .= plugin_cluster();
    # Prettify plugin cluster (not same rank)
    $out .= '    ' . join(' -> ', @last_node) . " [style=invis];\n";
    $out .= $in;

    # Write
    write_file $fp2, $out;
}


# Convert to png
sub convert {
    system <<EOF,
dot -Tsvg $fp2  > $fp3 && xdg-open $fp3
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


# Header
sub header { <<EOF;
digraph G {
    concentrate = true;
    fontsize = 15;
    splines = ortho;
    compound = true;
    label = "ABISM\nAdaptative Background Interactive Strehl Meter"
    labelloc = top;

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
