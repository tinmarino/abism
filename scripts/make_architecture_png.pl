# To make the architecture png
# TODO: abism.sh, abism.py
#       get script path
#       work with /tmp 
# Color combination https://color.adobe.com/fr/create?fbclid=IwAR3bPaJcPqxONgHms2YtJv4-gMK9CrijpLd6qNU2fpfeyF79YOXc4GJP9Nk

use v5.26;
use File::Basename qw/dirname/;
use Getopt::Long qw(GetOptions);
use File::Slurp qw/read_file write_file/;

my $fp1 = '/tmp/abism_1.dot';
my $fp2 = '/tmp/abism_2.dot';
my $fp3 = '/tmp/abism.svg';
my $in; my $do_pydep; my $do_transform; my $do_convert;
my @last_node;

GetOptions(
    'pydep' => \$do_pydep,
    'transform' => \$do_transform,
    'convert' => \$do_convert
    ) or die usage();

pydep() if $do_pydep;
transform() if $do_transform;
convert() if $do_convert;


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
sub transform{
    # Read
    $in = read_file $fp1;

    # Remove head
    $in =~ s/^[\s\S]*node \[.*\];\n*//;

    # Remove util
    $in =~ s/^.*\babism_(front_|back_)?(util|answer).*$//gm;

    # Replace main
    $in =~ s/^.*\babism___main__\s*\[.*$/node_main()/gme;
    $in =~ s/^.*\babism_run\s*\[.*$/node_run()/gme;

    # Remove empty lines
    $in =~ s/^\s*\n//gm;

    # Create output
    my $out = header();
    $out .= front_cluster();
    $out .= back_cluster();
    $out .= plugin_cluster();
    # Prettify pllugin cluster (not same rank)
    $out .= '    ' . join(' -> ', @last_node) . " [style=invis];\n";
    $out .= $in;

    # Write
    write_file $fp2, $out;
}

# Convert ot png
sub convert{
    system <<EOF,
dot -Tsvg $fp2  > $fp3 && xdg-open $fp3
EOF
}





sub nodes{
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
sub header{ <<EOF;
digraph G {
    concentrate = true;
	splines = ortho;
  	compound = true;
    label = "ABISM\nAdaptative Background Interactive Strehl Meter"
    labelloc = top;

    node [style=filled,fillcolor="#ffffff",
		  fontcolor="#000000",fontname=Helvetica,fontsize=10,
          rank="min",
	];
	edge [ overlap=true, color="#000000",  ]
    {rank = same;
    abism___main__ ->  abism_run;
    }
EOF
}

# Front
sub front_cluster{ "\n\n" . <<EOF;
subgraph cluster_front {
	label = "FrontEnd";
	fontcolor="#520C04";
	color="#520C04";
    penwidth=5;

${\nodes('abism_front', {
    'fillcolor' => '#D48A7D',
    'fontcolor' => '#000000'
})}
}
EOF
}

# Back
sub back_cluster{ "\n\n" . <<EOF;
subgraph cluster_back {
	label = "BackEnd";
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
	label = "Puglin";
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
sub node_main{ <<'EOF';
    abism___main__ [label="ABISM\nsh> abism\lsh> python path/to/clone/abism.py\lsh> python -m abism\lpy> from abism import __main__\l",
        shape=box, fillcolor="#ffffff",fontcolor="#000000"];
EOF
}


# Run
sub node_run{ <<'EOF';
    abism_run [label="run\npy>from abism.run import run_sync; run_sync()\lipy>from abism.run import run_async; sm = run_async()\l",
        shape=box, fillcolor="#ffffff",fontcolor="#000000"];
EOF
}
