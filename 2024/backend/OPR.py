from scipy.sparse import csr_array
import numpy as np
from scipy.linalg import lstsq
#from scipy.sparse.linalg import spsolve, norm
#from scipy.sparse.linalg import lsqr


class OPR: 
    @staticmethod
    def get_rows(m):
        yield m.alliances.red.team_keys, m.alliances.blue.team_keys, m.score_breakdown['red']['totalPoints'], m.score_breakdown['blue']['totalPoints']        

    def __init__(self, matches, teams: set):
        team_lookup = dict((k,i) for (i,k) in enumerate(teams))
        
        A_data = []
        row = []
        col = []
        b_OPR = []
        b_DPR = []
        b_TPR = []
        ctr = 0
        for m in map(OPR.get_rows, matches):
            for red_keys, blue_keys, red_score, blue_score in (m):                
                for t in red_keys:
                    row.append(len(b_OPR))
                    col.append(team_lookup[t])
                    A_data.append(1)
                b_OPR.append(red_score)
                b_DPR.append(blue_score)
                b_TPR.append(red_score-blue_score)
                for t in blue_keys:
                    row.append(len(b_OPR))
                    col.append(team_lookup[t])
                    A_data.append(1)
                b_OPR.append(blue_score)
                b_DPR.append(red_score)
                b_TPR.append(blue_score-red_score)

                
        A = csr_array((A_data, (row, col)), shape=(len(b_OPR), len(team_lookup)))
        # print(A.shape, b.shape )
        #x = spsolve(A, b)
        #x

        # Thanks ChatGPT!
        result = {}
        for (b, tag) in [(b_OPR, 'OPR'), (b_DPR, 'DPR'), (b_TPR, 'TPR')]:
            b = np.array(b)            
            x, residuals, rank, s = lstsq(A.todense(), b)
            RSS = residuals.sum()
            Rinv = np.linalg.inv(np.triu(s))
            err = np.mean(A@x-b)
            print(f'Error {tag}: {err}')
            
            sigmas = np.sqrt(RSS / (len(b) - len(x)) * np.diag(Rinv))
            result[tag] = (x, sigmas)
        #return_values = lsqr(A, b, calc_var=True)
        #result = return_values
        #print(result)
        #x = return_values[0]
        #var = return_values[-1]
        #print(var)

        #for t,opr,sigma in sorted(opr, key=lambda x: x[1], reverse=True):
        #    print(t,opr,sigma)

        #print((A@x).shape,b.shape)
        #print(A@x-b)
        #self.opr = [(t,x[i],sigmas[i]) for i,t in enumerate(teams)]
        self.opr_lookup = dict ([(t, {'ix':i}) for i,t in enumerate(teams)])
        for t in self.opr_lookup:
            self.opr_lookup[t]['opr'] = {'mu': result['OPR'][0][self.opr_lookup[t]['ix']], 'sigma': result['OPR'][1][self.opr_lookup[t]['ix']]}
            self.opr_lookup[t]['dpr'] = {'mu': result['DPR'][0][self.opr_lookup[t]['ix']], 'sigma': result['DPR'][1][self.opr_lookup[t]['ix']]}
            self.opr_lookup[t]['tpr'] = {'mu': result['TPR'][0][self.opr_lookup[t]['ix']], 'sigma': result['TPR'][1][self.opr_lookup[t]['ix']]}
        self.opr_lookup[''] = {'opr': {'mu': 0, 'sigma': 0}, 'dpr': {'mu': 0, 'sigma': 0}, 'tpr': {'mu': 0, 'sigma': 0}}

    def predict(self, red,blue, method='opr'):
        mu = []
        sigma = []
        for r in red:
            mu.append(self.opr_lookup[r][method]['mu'])
            sigma.append(self.opr_lookup[r][method]['sigma'])
        for b in blue:
            mu.append(-self.opr_lookup[b][method]['mu'])
            sigma.append(self.opr_lookup[b][method]['sigma'])
        mu = sum(mu)
        sigma = np.linalg.norm(sigma)
        return(mu,sigma)