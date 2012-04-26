#KTFormatter
Peter Swire
Swirepe.com

## What Does It Do
It takes your comma separated value-formatted data and turns it into a form more suitable for bayesian knowledge tracing.

## How Do You Use It
     usage: ktformatter [-h] -i INPUT -o OUTPUT -s SKILL -r RESPONSE -p STUDENT
                        [--header] [--train-percent TRAIN_PERCENT] [--tabs-in]
                        [--spaces-in] [--compress] [--split-by-skill]
                        [--split-by-student] [--tabs-out] [--spaces-out]
                        [--skills-as-int] [--students-as-int] [--kdd]
     
     Split a file up by skill -> responses, and by train/test
     
     optional arguments:
       -h, --help            show this help message and exit
       -i INPUT, --input INPUT
                             The CSV to chop up
       -o OUTPUT, --output OUTPUT
                             The directory to output files into
       -s SKILL, --skill SKILL
                             The column containing skill identifiers (starts at
                             zero)
       -r RESPONSE, --response RESPONSE
                             The column containing responses (starts at zero).
                             Note, responses need to be either 0 or 1.
       -p STUDENT, --student STUDENT
                             The column containing person ids (starts at zero)
       --header              The input csv contains a header that needs to be
                             stripped
       --train-percent TRAIN_PERCENT
                             The percent of the total data to put into a training
                             set.
       --tabs-in             Input with separator as tabs (default is commas)
       --spaces-in           Input with separator as spaces (default is commas)
       --compress            Compress the output files with gzip
       --split-by-skill      Output each skill separately
       --split-by-student    Output each student separately (implies --split-by-
                             skill)
       --tabs-out            Output with separator as tabs (default is commas)
       --spaces-out          Output with separator as spaces (default is commas)
       --skills-as-int       Convert skills into integer ids
       --students-as-int     Convert student ids into integer ids
       --kdd                 The KDD data has multiple skills in their skill
                             column, separated by ~~.
     
     KT Formatter: Turn csvs into files suited for training knowledge tracing models.
     2012 Peter Swire - swirepe.com
     
     Example - breaking up the kdd cup data:
         dataFormatter 
             --input bridge_to_algebra_2006_2007_train.txt
             --output bridge
             --student 1
             --skill 17
             --response 13 
             --header
             --tabs-in
             --split-by-skill
             --skills-as-int
             --students-as-int
             --kdd
             --compress
             
## What is Bayesian Knowledge Tracing?
Knowledge Tracing is the dominant model in educational data mining right now.  It's a dynamic Bayesian network, and the focus of most of my research.  The abstract to [this paper](https://github.com/swirepe/AllKT) should give you a little more detail than that.
