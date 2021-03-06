# Main file for usage of sGLMM (Sparse graph-structured linear mixed model)
# Cite information:
# Ye, W. Liu, X. Wang, H. & Xing, EP.
# A Sparse Graph-structrued Lasso Mixed model for genetic association with confounding correction
#

import sys
import numpy as np
from optparse import OptionParser, OptionGroup
from model.sGLMM import sGLMM
from utility.dataLoader import FileReader
sys.path.append('../')


def print_out_head(out): out.write("\t".join(["RANK", "SNP_ID", "EFFECT_SIZE_ABS"]) + "\n")


def output_result(out, rank, id, beta):
    out.write("\t".join([str(x) for x in [rank, id, beta]]) + "\n")


def run(opt, outFile):
    discoverNum = opt.snum
    numintervals = 500
    ldeltamin = -5
    ldeltamax = 5
    learningRate = 1e-5

    if (opt.lmbd is not None) and (opt.snum is not None):
        print 'Invalid options: lambda and snum cannot be set together.'
        exit(1)
    if opt.lmbd is None:
        lam = 0.7
    else:
        lam = float(opt.lmbd)
    cv_flag = ((opt.lmbd is None) and (opt.snum is None))

    # Get the input
    reader = FileReader(fileName=opt.fileName, fileType=opt.fileType, imputation=(not opt.missing))
    snps, Y, Xname = reader.readFiles()
    K = np.dot(snps, snps.T)
    # print snps.shape, Y.shape
    # beta_model_lmm = np.zeros((snps.shape[1], Y.shape[1]))

    # Run

    slmm_model = sGLMM(discoverNum=discoverNum, ldeltamin=ldeltamin, ldeltamax=ldeltamax, learningRate=learningRate,
                       numintervals=numintervals, lam=lam, threshold=opt.threshold, isQuiet=opt.quiet, cv_flag=cv_flag)
    beta_model_lmm = slmm_model.train(X=snps, K=K, y=Y)

    # There is an error
    if beta_model_lmm is None:
        print 'No legal effect size is found under this setting'
        exit(1)

    # Output the result to the file
    ind = np.where(beta_model_lmm != 0)[0]
    xname = []
    for i in ind:
        xname.append(i)


    beta_name = zip(beta_model_lmm, Xname)
    bn = sorted(beta_name)
    bn.reverse()

    out = open(outFile, 'w')
    print_out_head(out)

    for i in range(len(bn)):
        output_result(out, i + 1, bn[i][1], bn[i][0])

    out.close()

    print 'Computation ends normally, check the output file at', outFile

# Main entry
usage = """usage: %prog [options] -n fileName
This program provides the basic usage to sGLMM, e.g:
python sGLMM.py -n data/mice.plink
        """
parser = OptionParser(usage=usage)

dataGroup = OptionGroup(parser, "Data Options")
modelGroup = OptionGroup(parser, "Model Options")

## data options
dataGroup.add_option("-t", dest='fileType', default='plink', help="choices of input file type")
dataGroup.add_option("-n", dest='fileName', help="name of the input file")

## model options
modelGroup.add_option("--lambda", dest="lmbd", default=None,
                      help="The weight of the penalizer. If neither lambda or snum is given, cross validation will be run.")
# modelGroup.add_option("--gamma", dest="gamma", default=0.7,
#                       help="The weight of the penalizer. If neither lambda or snum is given, cross validation will be run.")
modelGroup.add_option("--snum", dest="snum", default=None,
                      help="the number of targeted variables the model selects. If neither lambda or snum is given, cross validation will be run.")
modelGroup.add_option("--threshold", dest="threshold", default=0.618,
                      help="The threshold to mask the weak genotype relatedness")
modelGroup.add_option('-q', action='store_true', dest='quiet', default=False, help='Run in quiet mode')
modelGroup.add_option('-m', action='store_true', dest='missing', default=False,
                      help='Run without missing genotype imputation')

## advanced options
parser.add_option_group(dataGroup)
parser.add_option_group(modelGroup)

(options, args) = parser.parse_args()

if len(args) != 0:
    parser.print_help()
    sys.exit()

outFile = options.fileName + '.output'

print 'Running ... '
run(options, outFile)


