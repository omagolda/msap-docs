#!/usr/bin/env perl
# Converts CoNLL-U to CoNLL-U Plus / Morphosyntactic features.
# Copyright © 2024 Dan Zeman <zeman@ufal.mff.cuni.cz>
# License: GNU GPL

use utf8;
use open ':utf8';
binmode(STDIN, ':utf8');
binmode(STDOUT, ':utf8');
binmode(STDERR, ':utf8');

# Print the initial declaration of columns.
print("\# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC MSFEATS\n");
while(<>)
{
    # Any pre-existing global.columns directive will be discarded.
    next if(m/^\#\s*global\.columns\s*=/);
    # Comment lines and empty lines will be just copied.
    # Node lines must be converted from 10 to 11 columns.
    if(m/^[0-9]/)
    {
        chomp;
        my @f = split(/\t/, $_);
        # The first nine columns will stay intact, but we must disassemble MISC.
        my $msfeats = '_';
        unless($f[9] eq '_')
        {
            my @misc = split(/\|/, $f[9]);
            my @msffunc = grep {m/^MSFFunc=/} (@misc);
            my @msfeats = map {my $x = $_; $x =~ s/^MSF//; $x} (grep {m/^MSF/ && !m/^MSFFunc=/} (@misc));
            my @nonmsf = grep {!m/^MSF/} (@misc);
            $f[9] = scalar(@nonmsf) ? join('|', @nonmsf) : '_';
            # Do not copy any MS features if this is a function word.
            # If it is not a function word but there are no features, use '|' instead of '_'.
            my $is_function_word = scalar(@msffunc) == 0 || $msffunc[0] ne 'MSFFunc=No';
            my $has_msfeats = scalar(@msfeats) > 0;
            $msfeats = $is_function_word ? '_' : $has_msfeats ? join('|', @msfeats) : '|';
            # Abstract nodes that have been created to represent subject MS features
            # must be attached in the basic MS tree (Udapi could only put them in the
            # enhanced graph).
            if($f[0] =~ m/\./ && !$is_function_word && $has_msfeats)
            {
                if($f[8] =~ m/^([0-9]+):(.+)$/)
                {
                    $f[6] = $1;
                    $f[7] = $2;
                }
            }
        }
        push(@f, $msfeats);
        # Pack the line again.
        $_ = join("\t", @f)."\n";
    }
    print;
}
