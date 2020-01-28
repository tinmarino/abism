# To make the architecture png
# TODO: abism.sh, abism.py
#       get script path
#       work with /tmp 

use v5.26;
use File::Slurp qw/read_file write_file/;

my $fp1 = '/tmp/abism_1.dot';
my $fp2 = '/tmp/abism_2.dot';
my $in;

# Create dot
sub pydep{
    system <<EOF;
pydeps  $0/../abism --rmprefix abism.front. abism.back. abism.plugin. abism. --exclude-exact abism.front abism.back abism.plugin --show-dot --reverse  --max-bacon=1 --cluster --noshow > $fp1
EOF
}


# Convert dot
sub convert{
    # Read
    $in = read_file $fp1;

    # Remove head
    $in =~ s/^[\s\S]*node \[.*\];\n*//;

    # Remove util
    $in =~ s/^.*\babism_(front_|back_)?util.*$//gm;

    # Create output
    my $out = header();
    $out .= front_cluster();
    $out .= back_cluster();
    $out .= plugin_cluster();
    $out .= $in;

    # Write
    write_file 'abism_2.dot', $out;
}


sub nodes{
    my $name = shift; my @res = ();
    while ($in =~ s/(^\s*$name\w* \[.*$)//m){
        push @res, $1;
    }
    my $res = join "\n", @res;
    $res =~ s/^\s*$//mg;
    print $res;
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
