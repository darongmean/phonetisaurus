#!/usr/bin/python
import re, operator, os
from collections import defaultdict
from calculateER import ErrorRater

def process_testset( testfile, wordlist_out, reference_out, verbose=False ):
    """
      Process the testfile, a normal dictionary, output a wordlist for testing,
      and a reference file for results evaluation.  Handles cases where a single
      word has multiple pronunciations.
    """
    
    if verbose: print "Preprocessing the testset dictionary file..."
    test_dict = defaultdict(list)
    for entry in open(testfile,"r"):
        word, pron = entry.strip().split("\t")
        test_dict[word].append(pron)

    wordlist_ofp  = open(wordlist_out,"w")
    reference_ofp = open(reference_out,"w")
    test_list = sorted(test_dict.iteritems(), key=operator.itemgetter(0))
    for entry in test_list:
        wordlist_ofp.write("%s\n"%entry[0])
        reference_ofp.write("%s\t%s\n"%(entry[0],"\t".join(entry[1])))
    wordlist_ofp.close()
    reference_ofp.close()
    return

def evaluate_testset( modelfile, wordlistfile, referencefile, hypothesisfile, verbose=False ):
    """
      Evaluate the Word Error Rate (WER) for the test set.
      Each word should only be evaluated once.  The word is counted as 
      'correct' if the pronunciation hypothesis exactly matches at least
      one of the pronunciations in the reference file.
      WER is then computed as:
         (1.0 - (WORDS_CORRECT / TOTAL_WORDS))
    """

    if verbose: print "Executing evaluation with command:"
    command = "../phonetisaurus-g2p -m %s -o -t %s > %s" % (modelfile, wordlistfile, hypothesisfile)
    if verbose: print command
    os.system(command)
    references = {}
    for entry in open(referencefile,"r"):
        parts = entry.strip().split("\t")
        word  = parts.pop(0)
        references[word] = parts
    for entry in open(hypothesisfile,"r"):
        word, score, hypothesis = entry.strip().split("\t")

    PERcalculator = ErrorRater()
    PERcalculator.compute_PER_phonetisaurus( hypothesisfile, referencefile, verbose=verbose )

    return
    
    
if __name__=="__main__":
    import sys, argparse


    example = """%s --modelfile someg2pmodel.fst --testfile test.dic --wordlist_out test.words --reference_out test.ref --hypothesisfile test.hyp""" % sys.argv[0]
    parser = argparse.ArgumentParser(description=example)
    parser.add_argument('--testfile',  "-t", help="The test file in dictionary format. 1 word, 1 pronunciation per line, separated by '\\t'.", required=True )
    parser.add_argument('--prefix',    "-p", help="Prefix used to generate the wordlist, hypothesis and reference files.  Defaults to 'test'.", required=False )
    parser.add_argument('--modelfile', "-m", help="Path to the phoneticizer model.", required=True )
    parser.add_argument('--verbose',   "-v", help='Verbose mode.', default=False, action="store_true")
    args = parser.parse_args()

    if args.verbose:
        for attr, value in args.__dict__.iteritems():
            print attr, value
    wordlist = "%s.words"%( args.prefix ); hyp_file = "%s.hyp"%(args.prefix); ref_file = "%s.ref"%(args.prefix)
    
    process_testset( args.testfile, wordlist, ref_file )
    evaluate_testset( args.modelfile, wordlist, ref_file, hyp_file, verbose=args.verbose ) 
