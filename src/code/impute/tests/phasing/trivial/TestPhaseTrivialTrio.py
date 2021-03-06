'''
============================================================
Test phasing algorithm for trivial Mendelian cases in
a trio.

Created on July 2, 2012
@author: Oren Livne <livne@uchicago.edu>
============================================================
'''
import unittest
from impute import impute_test_util as itu
from numpy.ma.testutils import assert_equal
from impute.data.problem import Problem
from impute.phasing.phase_trivial import trivial_phaser
from impute.data.constants import CHILD
from impute.data import io, io_genotype
from impute.impute_test_util import assert_problem_stats

class TestPhaseTrivialTrio(unittest.TestCase):
    #---------------------------------------------
    # Constants
    #---------------------------------------------
    
    #---------------------------------------------
    # Setup Methods
    #---------------------------------------------
    def setUp(self):
        '''Load test data and expected results.'''
        unittest.TestCase.setUp(self)
        # The way to load a pedigree in conjunction with a genotype set is to recode
        # its sample IDs to consecutive for easier access by phasers.
        self.problem = io.read_plink(prefix=itu.GENOTYPE_TRIO, haplotype=None, pedigree=itu.GENOTYPE_TRIO + '.tfam')
        self.phaser = trivial_phaser()
        
        # Expected results
        self.solution = Problem(self.problem.pedigree, io_genotype.read('plink', 'genotype', prefix=itu.GENOTYPE_TRIO_SOLUTION))

    #---------------------------------------------
    # Test Methods
    #---------------------------------------------
    def test_phase_trivial_cases(self):
        '''Check phasing trivial cases in trios. The trio data is (0,1=parents, 2=child). The
        solution is kept in the trio test file as the fictitious individual 3.'''
        g = self.problem.genotype
        itu.assert_size_equals(self.problem.genotype, 19, 3)
        assert_equal(self.problem.error.shape, (19, 3), 'Incorrect error array size')
        
        trio = (0, 1, 2)
        solution = self.solution.genotype.data
        h = self.problem.haplotype
        assert_problem_stats(self.problem, 6 * g.num_snps, 0, 0)
        self.phaser.run(self.problem)
        
        for snp in self.problem.snp_range:
            expected_parent_genotype = solution[snp, trio[0:CHILD], :]
            #expected_child_genotype  = solution[snp,trio[CHILD],:]
            expected_child_haplotype = solution[snp, trio[CHILD], :]
            parent_genotype = g.data[snp, trio[0:CHILD], :]
            #child_genotype  = g.data[snp,trio[CHILD]]
            child_haplotype = h.data[snp, trio[CHILD]]
            '''
            print 'SNP', snp
            print 'Data', g.data[snp,trio,:]
            print 'Imputed parent', parent_genotype
            print 'Child hap', child_haplotype
            print 'Solution hap', solution[snp,trio,:]
            '''
            assert_equal(child_haplotype, expected_child_haplotype, 'Wrong child haplotype by trivial phaser at snp %d' % (snp,))
            assert_equal(parent_genotype, expected_parent_genotype, 'Wrong parent genotype imputation by trivial phaser at snp %d' % (snp,))
            #assert_equal(np.sort(child_genotype), np.sort(expected_child_genotype), 'Wrong child genotype imputation by trivial phaser at snp %d' % (snp,))

        assert_problem_stats(self.problem, 6 * g.num_snps, 66, 6, error_rate=0.1)
        
    #---------------------------------------------
    # Private Methods
    #---------------------------------------------
