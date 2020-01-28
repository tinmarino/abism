# To make the architecture png
# TODO: abism.sh, abism.py
#       get script path
#       work with /tmp 

use v5.26;
use File::Basename qw/dirname/;
use Getopt::Long qw(GetOptions);
use File::Slurp qw/read_file write_file/;

my $fp1 = '/tmp/abism_1.dot';
my $fp2 = '/tmp/abism_2.dot';
my $fp3 = '/tmp/abism.svg';
my $in; my $do_pydep; my $do_transform; my $do_convert;

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
    $in =~ s/^.*\babism_(front_|back_)?util.*$//gm;

    # Remove empty lines
    $in =~ s/^\s*\n//gm;
    print $in;

    # Create output
    my $out = header();
    $out .= front_cluster();
    $out .= back_cluster();
    $out .= plugin_cluster();
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
    my $name = shift; my @res = ();
    while ($in =~ s/(^\s*$name\w* \[.*\n)//m){
        push @res, $1;
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

    node [style=filled,fillcolor="#ffffff",
		  fontcolor="#000000",fontname=Helvetica,fontsize=10,
          rank="min",
	];
	edge [ overlap=true, color="#000000",  ]
EOF
}

# Front
sub front_cluster{ "\n\n" . <<EOF;
subgraph cluster_front {
	label = "FrontEnd";
	color=blue;
    penwidth=5;

${\nodes('abism_front')}
}
EOF
}

# Back
sub back_cluster{ "\n\n" . <<EOF;
subgraph cluster_back {
	label = "BackEnd";
	color=red;
    penwidth=5;
    rank="min";

${\nodes('abism_back')}
}
EOF
}

# Plugin
sub plugin_cluster{ "\n\n" . <<EOF;
subgraph cluster_plugin {
	label = "Puglin";
	color=green;
    penwidth=5;
	rank="min";
	
${\nodes('abism_plugin')}
}
EOF
}
