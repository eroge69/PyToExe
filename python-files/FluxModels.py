import os, time, copy, numpy, libsbml, numpy, datetime, re, math
import keio2sbml, GAMSclasses, SBMLclasses, core
from GAMSclasses import file2tuple
from pylab import subplot, figure, show, xlabel, ylabel, title, plot, axis, errorbar, bar, savefig, subplots_adjust
import matplotlib
import shelve
from FluxMaps import FluxMap


#font = {'family' : 'normal',
#        'weight' : 'bold',
#        'size'   : 20}

font = {'size'   : 20}

matplotlib.rc('font', **font)


class FluxModel:
    "Base class to derive all others involved in 13C"
    
    def __init__(self,ReacNet,GAMSfileName,outputFuncs):
        # check for sbmls file type here?
        # Obtain GAMS file information
        try: 
            self.dirGAMSFile =  os.environ['QUANTMODELPATH']+'/'
        except KeyError:
            raise Exception('QUANTMODELPATH environment variable not set')
        gamsFile        = self.dirGAMSFile + GAMSfileName
        self.gamsFile   = gamsFile
        
        # Storing SBML file
        self.ReacNet = ReacNet

        # Loading output functions
        self.outputFuncs = outputFuncs
        
    def recordFluxes(self,fluxDict):
        """Fixes fluxes in solution in sbml file"""
        ReacNet = self.ReacNet
        reactionList = ReacNet.reactionList
        for reaction in reactionList:
            if reaction.name in fluxDict:
                reaction.flux = fluxDict[reaction.name]
           
        # Storing changes
        self.ReacNet  = SBMLclasses.ReactionNetwork(  (ReacNet.modelName,ReacNet.notes,ReacNet.metList,ReacNet.reactionList))


    def writeSBML(self,filename):
        "Write changes made in model to sbml file."
        ReacNet = self.ReacNet
        newReacNet = SBMLclasses.ReactionNetwork(  (ReacNet.modelName,ReacNet.notes,ReacNet.metList,ReacNet.reactionList))
        
        return newReacNet.write(filename)
       
        
    def runGAMSBatch(self,problemBatch):
        "General function for running a GAMS batch"
        
        with problemBatch as batch:
            # Run problem(s)
            batch.run()

            # Check if they are done
            batch.waitTilDone()
        
            # Collect data
            batch.collect()
        
            # Put results in local format 
            resultsDict = batch.getAllResults()
                
        
        return resultsDict          
        
    def runGAMSProblem(self,problem):
        "General function for solving a GAMS problem"
        
        # Using the 'with' statement to provide automatic setup and wrapup
        with problem as prob:
            # Run problem
            prob.run()

            # Check if it is done
            prob.waitTilDone()

            # Collect data
            prob.collect()
        
            # Output data 
            resultsDict = prob.Results            

        return resultsDict        
        
        
    def solveProblem(self,problem):
        """ Solves problem stored in self.problem. This can be a single GAMS problem or a GAMS problem batch"""
        # Determine what kind of problem we have
        self.problem = problem
        if problem.__class__.__name__== 'GAMSproblem':
            resultsDict = self.runGAMSProblem(problem)
        elif problem.__class__.__name__== 'GAMSproblemBatch':
            resultsDict = self.runGAMSBatch(problem)
            
        return resultsDict
        
    def convMetName(self,met):
        """Converts the metabolite name to standard format as defined in reaction network"""    
        return self.ReacNet.convMetName(met)
    
    def convRxnName(self,rxn):
        """Converts the reaction name to standard format as defined in reaction network"""
        return self.ReacNet.convRxnName(rxn)    

class FBAModel(FluxModel):
    "Class for FBA calculations, sbmlFileName can be name of a file or file in string format."
    def __init__(self,sbmlFileName):
        # Obtain GAMS file information
        try: 
            dirGAMSFile =  os.environ['QUANTMODELPATH']+'/' 
        except KeyError:
            raise Exception('QUANTMODELPATH environment variable not set')
        GAMSfileName     = "GAMS_EMU_MFA_FLUX_FBA.gms"
        GAMSFVAfileName  = "GAMS_EMU_MFA_FLUX_FVA.gms"
        gamsFile         = dirGAMSFile + GAMSfileName
        gamsFileFVA      = dirGAMSFile + GAMSFVAfileName
        self.gamsFile    = gamsFile
        self.gamsFileFVA = gamsFileFVA
        
        # Reading SBML file
        ReacNet       = SBMLclasses.ReactionNetwork(sbmlFileName)
        self.ReacNet  = ReacNet

        # Loading output functions
        outputFuncs = {'Info':(infoOut,['OFGenInfo.txt']),
                       'Vout':(GAMSclasses.parOut,['VFBAout.txt','Vout']), 
                       'Successful':(getSuccessful,[GAMSfileName.replace('.gms','.lst',1)]),
                        }
        self.outputFuncs = outputFuncs
        outputFuncsFVA = {'Info':(infoOut,['OFGenInfo.txt']),
                          'Vout':(GAMSclasses.parOut,['VFBAout.txt','Vout']), 
                          'Vmax':(GAMSclasses.parOut,['Vmaxout.txt','Vmax']), 
                          'Vmin':(GAMSclasses.parOut,['Vminout.txt','Vmin']), 
                        }
        self.outputFuncsFVA = outputFuncsFVA
        
    def getGAMSInputFiles(self): # TODO Convert to getGAMSInputFilesFBA as soon as changeFluxBoundsFAST 
        return self.ReacNet.getStoichMetRxnFBAFiles()
        

    def findFluxes(self,erase=True,warnFail=True):  
        # Get problem
        gamsFile            = self.gamsFile
        outputFuncs         = self.outputFuncs
        self.GAMSInputFiles = self.getGAMSInputFiles()  
        Name                = 'FBAprob' 
               
        GAMSprob       = GAMSclasses.GAMSproblem(Name,gamsFile,self.GAMSInputFiles,outputFuncs,type='serial')        
        GAMSprob.erase = erase     # TODO: write as an argument in line above
        
        resultsDict = self.solveProblem(GAMSprob)
        
        results     = FBAResults(resultsDict,self.ReacNet)   
        
        # Warn if LP failed
        if warnFail:
            results.printSuccess()
            
        return results

    def FVA(self,reactions='default',erase=True):  # TODO: a parallel version of this
        """Method for Flux Variability Analysis"""
                  
        # Get problem
        gamsFile    = self.gamsFileFVA
        ReacNet     = self.ReacNet
        outputFuncs = self.outputFuncsFVA
        Name        = 'FBAprob'
        
        GAMSInputFilesFVA = ReacNet.getStoichMetRxnFVAFiles(studiedReactions = reactions)
        GAMSprob       = GAMSclasses.GAMSproblem(Name,gamsFile,GAMSInputFilesFVA,outputFuncs)
        GAMSprob.erase = erase     # TODO: write as an argument in line above

        resultsDict = self.solveProblem(GAMSprob)
            
        results     = FVAResults(resultsDict,self.ReacNet)        

        return results


    def changeFluxBoundsFAST(self,reactionName,flux):   # TODO: these two methods are not needed anymore. Test they are unnecessary and eliminate
        "Changes flux bounds for problem without having to change whole sbml file (takes too long). This could be done in a more elegant way."
        
        fileNameUB   = 'ubvec.txt'
        fileNameLB   = 'lbvec.txt'
      
        reactionList = self.ReacNet.reactionList
        reactDict = reactionList.getReactionDictionary()
        reactDict[reactionName].fluxBounds = flux

        UBPar = reactionList.getUB()
        LBPar = reactionList.getLB()
              
        stUB = UBPar.write('toString')
        stLB = LBPar.write('toString')
        
        self.GAMSInputFiles[3] = (fileNameUB,stUB)
        self.GAMSInputFiles[4] = (fileNameLB,stLB)
        
        # Keeping changes in a list for later use with recordFASTchanges
        if hasattr(self,'FASTchanges'):
            self.FASTchanges[reactionName] = flux
        else:
            FASTchanges = {reactionName : flux}
            self.FASTchanges = FASTchanges
            
        
    def recordFASTchanges(self):
        "Permanently records in the sbml file and tuple the changes from changeFluxBoundsFAST"
        # TODO: I think this slows things down a lot, see if it can be eliminated
        for reactionName in self.FASTchanges:    # This for loop should go
            # Change Tuple
            reacDict = self.ReacNet.reactionList.getReactionDictionary()
            reaction = reacDict[reactionName]
            reaction.fluxBounds = self.FASTchanges[reactionName]
            
        # Updating tuple
        self.ReacNet = SBMLclasses.ReactionNetwork( (self.ReacNet.modelName, self.ReacNet.notes, self.ReacNet.metList, self.ReacNet.reactionList))
        
        
    def changeObjective(self,reactionName,cval):
        "Changes objective value."
        reactionList = self.ReacNet.reactionList
        reactDict = reactionList.getReactionDictionary()
        reactDict[reactionName].cval = cval
        
       
                
        
        
class C13Model(FluxModel):
    "Class for 13C MFA calculations"
    
    def __init__(self,sbmlFileName):
        # GAMS file name
        GAMSfileName    = "GAMS_EMU_MFA_FLUX.gms"            # TODO: change this to a method: getGAMSFileRnd
        infeasFileName  = GAMSfileName.replace('gms','lst')     
        
        # sbml file
        ReacNet      = SBMLclasses.C13ReactionNetwork(sbmlFileName)


        # Loading output functions
        outputFuncs = {'Info'           :(infoOut           ,['OFGenInfo.txt']),
                       'Vout'           :(fluxParOut        ,['Vout.txt','Vout']), 
                       'fout'           :(GAMSclasses.parOut,['fout.txt','fout']),
                       'labelcomp'      :(labelingParOut    ,['labelcomp.txt','labelcomp']),
                       'infeasibilities':(getInfeasibilities,[infeasFileName])    
                        }
                        
        self.getFilesFunctionName    = 'get13CMFAfiles'
        #self.resultsFunctionName = 'C13Results'
        self.resultsFunctionNameRand = 'C13Results'
        self.resultsFunctionNameVar  = 'C13FVAResults'
        
        FluxModel.__init__(self,ReacNet,GAMSfileName,outputFuncs)


    def getGAMSInputFiles(self,ReacNet,labelMin=0.99,vSuggested='default',procString='raw'):
        # Get Input Files for the GAMS problem. 
        # I separated this from createBatch for flexibility
        
        GAMSInputFiles       = ReacNet.get13CMFAfiles(vSuggested=vSuggested, labelCompNormMin=labelMin, procString= procString)       
        
        return GAMSInputFiles      
      
    def createBatchRand(self,Nrep,Nrand,labelMin,maxFlux13C,erase,procString='raw'):     # TODO: Take maxFlux13C and labelMin to GAMS file class?
        # Create Batch of gams problems
        ReacNet     = self.ReacNet
        ReacNetOrig = copy.deepcopy(ReacNet)
        gamsFile = self.getGAMSFileRand(maxFlux13C)
        #gamsFile    = self.gamsFile
        #if maxFlux13C:         
        #    gamsFile = substituteInFile(gamsFile,[('maxflow13CU',maxFlux13C)]) 
        outputFuncs = self.getOutputFuncsRand()                
        #outputFuncs = self.outputFuncs    

        problems = []
        for i in range(Nrand+1):
            for j in range(1,Nrep+1):
                Name    = '/Run'+str(i)+'_'+str(j)
                dirName = os.getcwd()+Name
                
                GAMSInputFiles = self.getGAMSInputFiles(ReacNet,labelMin,procString=procString)  # TO DO: put this out of the loop
                GAMSprob       = GAMSclasses.GAMSproblem(Name,gamsFile,GAMSInputFiles,outputFuncs,directory = dirName)
                GAMSprob.erase = erase     # TODO: write as an argument in line above
                
                problems.append(GAMSprob)
                    
            ReacNet = copy.deepcopy(ReacNetOrig)
            ReacNet.randomizeLabeling()

        batch = GAMSclasses.GAMSproblemBatch(problems)
        batch.erase = erase     # TODO: write as an argument in line above. There should be no need to repeat this info
    
        return batch

    def createBatchVar(self,Nrep,fluxNames,labelMin,maxFlux13C,erase,procString='raw'):
        # Create Batch of gams problems  

        # Find best solution through findFluxesStds and save as suggested fluxes
        #resultsOne        = self.findFluxesStds(Nrep=Nrep,Nrand=0,erase=erase,limitFlux2Core=False)    
        # Adding previously calculated flux profile starting point for range procedure         
        vSuggested,resultsOne = self.getSuggestedFluxes(Nrep, erase, procString)

        # Record fits 
        self.recordFits(resultsOne.EMUlabel)
        
        # Change MDV stds to match best fit
        self.ReacNet.changeStds('toFits')     
        
        # GAMS file
        gamsFileVar = self.getGAMSFileVar(maxFlux13C)  
        #if maxFlux13C:         
        #    gamsFileVar = substituteInFile(gamsFileVar,[('maxflow13CU',maxFlux13C)])

        # Loading output functions
        outputFuncsVar = self.getOutputFuncsVar()        
        
        # Creating gams problems and storing them in a batch class    
        problems = []
        GAMSInputFilesCommon = self.getGAMSInputFiles(self.ReacNet,labelMin,vSuggested=vSuggested,procString=procString)            
        for fluxName in fluxNames:
            # Changing reaction name to sbml
            tmpRxn  = core.reaction(fluxName)
            fluxNameNew = tmpRxn.convNameStd2SBML()    #TODO: all name changing should be done just once at the inputs
            #fluxNameNew = self.convRxnName(fluxName)
            #fluxNameNew = fluxName
            Name    = '/Run_'+fluxNameNew
            dirName = os.getcwd()+Name
                                      
            # Add file for flux to focus on
            fluxFocus         = GAMSclasses.GAMSset('fluxFocus',set([fluxName]))
            fluxFocusSt       = fluxFocus.write('toString')
            fluxFocusFileName = 'fluxFocus.txt' 
            
            GAMSInputFiles = copy.deepcopy(GAMSInputFilesCommon)
            GAMSInputFiles.extend([(fluxFocusFileName,fluxFocusSt)])
        
            # Creating GAMS problem
            GAMSprob  = GAMSclasses.GAMSproblem(Name,gamsFileVar,GAMSInputFiles,outputFuncsVar)
            GAMSprob.erase = erase    
            GAMSprob.dir   = dirName
            problems.append(GAMSprob)         
        
        batch = GAMSclasses.GAMSproblemBatch(problems)
        
        return batch,resultsOne


    def getSuggestedFluxes(self,Nrep,erase,procString):
        """Obtains suggested fluxes for createBatchVar"""

       # Find best solution through findFluxesStds and save as suggested fluxes
        resultsOne        = self.findFluxesStds(Nrep=Nrep,Nrand=0,erase=erase,procString=procString)    
            
        # Adding previously calculated flux profile starting point for range procedure         
        self.ReacNet.reactionList.addFluxes(resultsOne.rangedFluxDict)
        fitFluxes    = fluxGAMSpar('vSUGG',[],fluxDict=self.ReacNet.reactionList.getFluxDictionary(level=2,rangeComp='best'))
        
        vSuggested = tuple([fitFluxes])
        
        return vSuggested,resultsOne 

    def GAMSFileModifications(self,gamsFile,maxFlux13C,maxTime):
        "Does standard modifitations for GAMS file"
        
        biomassReaction = self.ReacNet.reactionList.getBiomassReaction()
        if biomassReaction:            
            changes = [['BiomassEcoli',biomassReaction.name]]   # Change biomass reaction
        else: 
            changes = []
        
        if maxFlux13C:
            #changes.append(['maxflow13CU',maxFlux13C])
            changes.append(['maxflow13CU = (\d+)','maxflow13CU = '+str(maxFlux13C)])
            
        if maxTime:
            changes.append(['reslim = (\d+)','reslim = '+str(maxTime)])

       
        gamsFile = substituteInFile(gamsFile,changes) 
        
        return gamsFile

    def getGAMSFileRand(self,maxFlux13C,maxTime=[]):
        "Returns GAMS file for the ranged fluxes approach"
        gamsFileRand  = file2tuple(self.dirGAMSFile+'GAMS_EMU_MFA_FLUX.gms')        
        gamsFileRand  = self.GAMSFileModifications(gamsFileRand,maxFlux13C,maxTime)      
        
        return gamsFileRand

    def getGAMSFileVar(self,maxFlux13C,maxTime=[]):
        "Returns GAMS file for the ranged fluxes approach"
        gamsFileVar  = file2tuple(self.dirGAMSFile+'GAMS_EMU_MFA_FLUXvar.gms')        
        gamsFileVar  = self.GAMSFileModifications(gamsFileVar,maxFlux13C,maxTime)      
        
        return gamsFileVar
        
    def getOutputFuncsRand(self):
        """Returns output functions for randomization  approach"""
        
        # GAMS file name
        #GAMSfileName    = "GAMS_EMU_MFA_FLUX.gms"            # TODO: change this to a method: getGAMSFileRnd
        GAMSfileName    = self.getGAMSFileRand([])[0]
        infeasFileName  = GAMSfileName.replace('gms','lst')     


        # Loading output functions
        outputFuncs = {'Info'           :(infoOut           ,['OFGenInfo.txt']),
                       'Vout'           :(fluxParOut        ,['Vout.txt','Vout']), 
                       'fout'           :(GAMSclasses.parOut,['fout.txt','fout']),
                       'labelcomp'      :(labelingParOut    ,['labelcomp.txt','labelcomp']),
                       'infeasibilities':(getInfeasibilities,[infeasFileName])    
                        }
                                
        return outputFuncs        
        
    def getOutputFuncsVar(self):
        """Returns output functions for ranged fluxes approach"""
        
        # Loading output functions
        #GAMSfileName    = "GAMS_EMU_MFA_FLUXvar.gms"
        GAMSfileName    = self.getGAMSFileVar([])[0]
        infeasFileName  = GAMSfileName.replace('gms','lst')   
        outputFuncsVar = {
                       'Info'           :(infoOut           ,['OFGenInfo.txt']),      # Temporary. This should be set in init
                       'InfoMax'        :(infoOut           ,['OFGenInfoMax.txt']),      
                       'InfoMin'        :(infoOut           ,['OFGenInfoMin.txt']),  
                       'Vout'           :(fluxParOut        ,['Vout.txt','Vout']), 
                       'Vmaxout'        :(fluxParOut        ,['Vmaxout.txt','Vmaxout']), 
                       'Vminout'        :(fluxParOut        ,['Vminout.txt','Vminout']), 
                       'fout'           :(GAMSclasses.parOut,['fout.txt','fout']),
                       'labelcomp'      :(labelingParOut    ,['labelcomp.txt','labelcomp']),
                       'labelcompMax'   :(labelingParOut    ,['labelcompMax.txt','labelcompMax']),
                       'labelcompMin'   :(labelingParOut    ,['labelcompMin.txt','labelcompMin']),
                       'infeasibilities':(getInfeasibilities,[infeasFileName]),
                       'fluxBounds':(GAMSclasses.parOut,['fluxBounds.txt','fluxBounds'])        
                        }
                        
        return outputFuncsVar
        
        

    def getResultsStds(self,resultsDict):
        "Produces results out of the results dictionary"        
        results     = C13Results(resultsDict,self.ReacNet)           

        return results
        
    def getResultsRanges(self,resultsDict,resultsOne):
        "Produces results out of the results dictionary"        
        resultsVar     = C13FVAResults(resultsDict,self.ReacNet)
        rangedFluxDict = resultsOne.rangedFluxDict
        
        # Use the resultsOne solution (best fit) as a basis
        results = copy.deepcopy(resultsVar)
        results.rangedFluxDict = resultsOne.rangedFluxDict
        results.EMUlabel = resultsOne.EMUlabel
        results.OF = resultsOne.OF

        # Use the results of the 13C FVA to obtain confidence intervals
        for name in rangedFluxDict:
            if name in resultsVar.rangedFluxDict:
                rangedFluxDict[name].net.hi   = resultsVar.rangedFluxDict[name][1] 
                rangedFluxDict[name].net.lo   = resultsVar.rangedFluxDict[name][0]
                
                rangedFluxDict[name].forward  = 'NA'
                rangedFluxDict[name].backward = 'NA'
                rangedFluxDict[name].exchange = 'NA'
         
        # TODO: there is probably no reason to store this here anymore. Eliminate! 
        results.rangedFluxDict = rangedFluxDict
        
        # Storing result in reaction list
        results.ReacNet.reactionList.addFluxes(results.rangedFluxDict)       

        return results
        

    def findFluxesStds(self,Nrep=20,Nrand=5,erase=True,labelMin=0.99,maxFlux13C=[],procString='raw'):
        "Calculates fluxes and calculates confidence intervals through the monte carlo approach"        
        # Create directory and move into it
        self.origDir     = os.getcwd()
        self.baseDirName = time.strftime("%Y%m%dT%H%M%SGAMSstd")
        os.mkdir(self.baseDirName)
        os.chdir(self.baseDirName)
        
        # Get batch
        batch = self.createBatchRand(Nrep,Nrand,labelMin,maxFlux13C,erase,procString=procString)

        # Solve batch problem
        resultsDict = self.solveProblem(batch)
        
        results     = self.getResultsStds(resultsDict)
                
        # Delete Directory. There should be no files left inside
        os.chdir('..')
        if erase:
            os.rmdir(self.baseDirName)

        return results            
            
#    def findFluxesRangesOLD(self,Nrep,fluxNames,erase=True,labelMin=0.99,maxFlux13C=[]):
#        "Calculates fluxes and calculates confidence intervals through the optimization approach"        
#
#        #####
#        # Find best solution through findFluxesStds and save as initial suggested fluxes
#        resultsOne      = self.findFluxesStds(Nrep=Nrep,Nrand=0,erase=erase,labelMin=labelMin,maxFlux13C=maxFlux13C)            
#        rangedFluxDict  = resultsOne.rangedFluxDict
#        EMUlabel        = resultsOne.EMUlabel
#        OF              = resultsOne.OF
#        
#        self.ReacNet.reactionList.addFluxes(rangedFluxDict)
#        fitFluxes = fluxGAMSpar('vSUGG',[],fluxDict=self.ReacNet.reactionList.getFluxDictionary(level=2,rangeComp='best'))
#
#        # Record fits
#        self.recordFits(resultsOne.EMUlabel)
#        fragDict = self.ReacNet.fragDict()             # Saving the fits in frag.MDVfit. This could probably be included in recordFits
#        
#        # Change MDV stds to match best fit
#        oldReacNet = copy.deepcopy(self.ReacNet)
#        dataTypes = ['GCMS','CEMS','LCMS']
#        for type in dataTypes:
#            if type in self.ReacNet.notes:
#                data = self.ReacNet.notes[type]
#                for abbrev in data:
#                    newFrag = data[abbrev]
#                    frag    = fragDict[abbrev]
#                    newFrag.std = numpy.maximum(abs(frag.MDV-frag.MDVfit),newFrag.std)
#
#
#        #####
#        # Create flux variability GAMS problem
#        self.origDir     = os.getcwd()
#        self.baseDirName = time.strftime("%Y%m%dT%H%M%SGAMS")
#        os.mkdir(self.baseDirName)
#        os.chdir(self.baseDirName)
#      
#        # Get batch
#        batch = self.createBatchVar(fluxNames,fitFluxes,labelMin,maxFlux13C,erase)
#        #batch = self.createBatchVar(Nrep,Nrand,self.origDir,self.baseDirName,labelMin,maxFlux13C,erase)      
#        
#        # Solve batch problem
#        resultsDict = self.solveProblem(batch)
#        resultsVar     = self.getResultsRanges(resultsDict)
#        
#        #####
#        # Further processing of results
#        # TODO: insert this in 13CFVAresults? or may in getResultsRanges?
#        results = copy.deepcopy(resultsVar)      # Do we really want this to be a deepcopy?
#        results.rangedFluxDict = rangedFluxDict
#        results.EMUlabel = EMUlabel
#        results.OF = OF 
#        
#        for name in rangedFluxDict:
#            if name in resultsVar.rangedFluxDict:
#                rangedFluxDict[name].net.hi = resultsVar.rangedFluxDict[name][1]
#                rangedFluxDict[name].net.lo = resultsVar.rangedFluxDict[name][0]
#                
#                rangedFluxDict[name].forward  = 'NA'
#                rangedFluxDict[name].backward = 'NA'
#                rangedFluxDict[name].exchange = 'NA'           
#
#        results.rangedFluxDict = rangedFluxDict
#        
#        # Going back to initial ReacNet (with original stds)
#        self.ReacNet = oldReacNet
#
#        return results
       
    def findFluxesRanges(self,Nrep,fluxNames,erase=True,labelMin=0.99,maxFlux13C=[],procString='raw'):
        "Finds fluxes and ranges of fluxes within allowable Objective Function"
        baseDirName = time.strftime("%Y%m%dT%H%M%SGAMSrng")
        os.mkdir(baseDirName)
        os.chdir(baseDirName)
        
        oldReacNet = self.ReacNet 
         # Get batch
        batch,resultsOne = self.createBatchVar(Nrep,fluxNames,labelMin,maxFlux13C,erase,procString=procString)
        batch.erase = erase     # TODO: write as an argument in line above. There should be no need to repeat this info        

        # Solve batch problem
        resultsDict = self.solveProblem(batch)
        results  = self.getResultsRanges(resultsDict,resultsOne)
        
        # Going back to initial ReacNet (with original stds)
        self.ReacNet = oldReacNet
        #self.ReacNet.changeStds(oldReacNet.fragDict())   # this should be the final version

        # Delete Directory. There should be no files left inside
        os.chdir('..')
        if erase:
            os.rmdir(baseDirName)
            
        return results       
       
        
    def recordFits(self,EMUlabel):
        "Records fits to experimental data in SBML file"
        Notes        = self.ReacNet.notes       
        
        regexp = re.compile('(\D+)(\d+)')

        fragDictBasic = core.fragDictBasic()
        GCMS = {}
        LCMS = {}
        CEMS = {}
        for abbrev in EMUlabel:
            if abbrev in fragDictBasic:
                MDV       = EMUlabel[abbrev]
                fragment  = fragDictBasic[abbrev]
                className = fragment.__class__.__name__

                if className == 'GCMSfragment':                  
                    match = regexp.match(abbrev)
                    fragmentName = 'M-'.join(match.groups())
                    GCMS[abbrev] = core.GCMS(dataTup=(fragmentName,MDV,[]))                    
#                    GCMS[abbrev] = core.GCMS(rawMDV=MDV,fragment=fragmentName)
                if className == 'LCMSfragment':
                    fragmentName = fragment.abbrev
                    LCMS[abbrev] = core.LCMS(dataTup=(fragmentName,MDV,[]))
#                    LCMS[abbrev] = core.LCMS(rawMDV=MDV,fragment=fragmentName)
                if className == 'CEMSfragment':
                    fragmentName = fragment.abbrev
                    CEMS[abbrev] = core.CEMS(dataTup=(fragmentName,MDV,[]))
#                    CEMS[abbrev] = core.CEMS(rawMDV=MDV,fragment=fragmentName)
            else:
                raise Exception("Fragment "+abbrev+" not found in fragDictBasic")

        if GCMS:
            Notes['GCMS(fit)'] = GCMS
        if LCMS:
            Notes['LCMS(fit)'] = LCMS            
        if GCMS:
            Notes['CEMS(fit)'] = CEMS

        #return self.ReacNet.fragDict() 


class TwoSC13Model(C13Model):
    "Class for 2S-13CMFA calculations"
    
    def __init__(self,sbmlFileName):
        # GAMS file name
        GAMSfileName    = "GAMS_EMU_MFA_FLUX_HYB.gms"
        infeasFileName  = GAMSfileName.replace('gms','lst')     

        # sbml file
        ReacNet      = SBMLclasses.TSReactionNetwork(sbmlFileName)

        
        # Loading output functions
        outputFuncs = {'Info'           :(infoOut,['OFGenInfo.txt']),
                       'Vout'           :(fluxParOut,['Vout.txt','Vout']), 
                       'fout'           :(GAMSclasses.parOut,['fout.txt','fout']),
                       'labelcomp'      :(labelingParOut    ,['labelcomp.txt','labelcomp']),
                       'infeasibilities':(getInfeasibilities,[infeasFileName]),    
                       'VFBAout'        :(fluxParOut,['VFBAout.txt','VFBAout']), 
                       'VFBAgrowthout'  :(fluxParOut,['VFBAgrowthout.txt','VFBAgrowthout']), 
                       'Vgrowthout'     :(fluxParOut,['Vgrowthout.txt','Vgrowthout']), 
                        }
        
        self.getFilesFunctionName    = 'getTwoS13CMFAfiles'
        self.resultsFunctionNameRand = 'TSResults'
        self.resultsFunctionNameVar  = 'TSFVAResults'


        FluxModel.__init__(self,ReacNet,GAMSfileName,outputFuncs)

    def getGAMSInputFiles(self,ReacNet,labelMin=0.99,vSuggested='default',procString='raw'):
        # Get Input Files for the GAMS problem. 
        # I separated this from createBatch for flexibility
        
        GAMSInputFiles       = ReacNet.getTwoS13CMFAfiles(vSuggested=vSuggested, labelCompNormMin=labelMin, procString=procString)       
        
        return GAMSInputFiles 
         

    def getSuggestedFluxes(self,Nrep,erase,procString):
        """Obtains suggested fluxes for createBatchVar"""

       # Find best solution through findFluxesStds and save as suggested fluxes
        resultsOne        = self.findFluxesStds(Nrep=Nrep,Nrand=0,erase=erase,limitFlux2Core=False,procString=procString)    
    
        
        # Adding previously calculated flux profile starting point for range procedure         
        self.ReacNet.C13ReacNet.reactionList.addFluxes(resultsOne.rangedFluxDict)
        fitFluxes    = fluxGAMSpar('vSUGG',[],fluxDict=self.ReacNet.C13ReacNet.reactionList.getFluxDictionary(level=2,rangeComp='best'))
        self.ReacNet.reactionList.addFluxes(resultsOne.rangedFluxDictAll)       
        fitFluxesFBA = fluxGAMSpar('vFBASUGG',[],fluxDict=self.ReacNet.reactionList.getFluxDictionary(level=1,rangeComp='best'))
        
        vSuggested = (fitFluxes,fitFluxesFBA)
        
        return vSuggested,resultsOne 

    def getGAMSFileRand(self,maxFlux13C,maxTime=[]):
        "Returns GAMS file for the ranged fluxes approach"
        gamsFileRand  = file2tuple(self.dirGAMSFile+'GAMS_EMU_MFA_FLUX_HYB.gms')        
        gamsFileRand  = self.GAMSFileModifications(gamsFileRand,maxFlux13C,maxTime)      
        
        return gamsFileRand

    def getGAMSFileVar(self,maxFlux13C,maxTime=[]):
        "Returns GAMS file for the ranged fluxes approach"
        gamsFileVar  = file2tuple(self.dirGAMSFile+'GAMS_EMU_MFA_FLUX_HYBvar.gms')        
        gamsFileVar  = self.GAMSFileModifications(gamsFileVar,maxFlux13C,maxTime)      
        
        return gamsFileVar

#    def getGAMSFileVar(self):
#        "Returns GAMS file for the ranged fluxes approach"
#        dirGAMSFile =  os.environ['QUANTMODELPATH']+'/code/core/python_emu_gams/'    # TODO: This should be set in init
#        gamsFileVar  = file2tuple(dirGAMSFile+'GAMS_EMU_MFA_FLUX_HYBvar.gms')        
#        
#        return gamsFileVar
    
    
    def getOutputFuncsRand(self):
        """Returns output functions for randomization  approach"""
        
        # GAMS file name
        #GAMSfileName    = "GAMS_EMU_MFA_FLUX.gms"            # TODO: change this to a method: getGAMSFileRnd
        GAMSfileName    = self.getGAMSFileRand([])[0]
        infeasFileName  = GAMSfileName.replace('gms','lst')     

        # Start with the ones for 13C MFA
        outputFuncsRand = C13Model.getOutputFuncsRand(self)   
        
        # Add functions relevant to 2S only
        GAMSfileName    = "GAMS_EMU_MFA_FLUX_HYB.gms"          # TODO: clean this up by using getGAMSFileVar above
        infeasFileName  = GAMSfileName.replace('gms','lst')   

        outputFuncsRand['infeasibilities'] = (getInfeasibilities,[infeasFileName])
        outputFuncsRand['VFBAout']         = (fluxParOut        ,['VFBAout.txt','VFBAout'])
        outputFuncsRand['VFBAgrowthout']   = (fluxParOut        ,['VFBAgrowthout.txt','VFBAgrowthout'])
        outputFuncsRand['Vgrowthout']      = (fluxParOut        ,['Vgrowthout.txt','Vgrowthout'])
       
        
        return outputFuncsRand
            
    
    def getOutputFuncsVar(self):
        """Returns output functions for ranged fluxes approach"""
        
        # Start with the ones for 13C MFA
        outputFuncsVar = C13Model.getOutputFuncsVar(self)       
        
        # Add functions relevant to 2S only
        GAMSfileName    = "GAMS_EMU_MFA_FLUX_HYBvar.gms"          # TODO: clean this up by using getGAMSFileVar above
        infeasFileName  = GAMSfileName.replace('gms','lst')   

        outputFuncsVar['infeasibilities'] = (getInfeasibilities,[infeasFileName])
        outputFuncsVar['VFBAout']         = (fluxParOut        ,['Vout.txt','Vout'])
        outputFuncsVar['VFBAmaxout']      = (fluxParOut        ,['VFBAmaxout.txt','VFBAmaxout'])
        outputFuncsVar['VFBAminout']      = (fluxParOut        ,['VFBAminout.txt','VFBAminout'])
        outputFuncsVar.pop('Vmaxout')
        outputFuncsVar.pop('Vminout')
        
        return outputFuncsVar
        
        

    def getResultsStds(self,resultsDict):
        "Produces results out of the results dictionary"        
        results     = TSResults(resultsDict,self.ReacNet)           

        results.ReacNet.C13ReacNet.reactionList.addFluxes(results.rangedFluxDict)
        results.ReacNet.reactionList.addFluxes(results.rangedFluxDictAll)

        return results
        
    def getResultsRanges(self,resultsDict,resultsOne):
        "Produces results out of the results dictionary"    
        # TODO: compact this with the C13 model version
        resultsVar        = TSFVAResults(resultsDict,self.ReacNet)           
        rangedFluxDictAll = resultsOne.rangedFluxDictAll
        rangedFluxDict    = resultsOne.rangedFluxDict
        inFluxRef         = self.ReacNet.inFluxRef


        # Further processing of results  
        #TODO: May be move to TSFVAresults?
        #rangedFluxDictAll = resultsOne.rangedFluxDictAll


        # Use the resultsOne solution (best fit) as a basis
        results = copy.deepcopy(resultsVar)
        results.rangedFluxDict = resultsOne.rangedFluxDict
        results.rangedFluxDictAll = resultsOne.rangedFluxDictAll
        results.EMUlabel = resultsOne.EMUlabel
        results.OF = resultsOne.OF   

        # Use the results of the 13C FVA to obtain confidence intervals
        for name in rangedFluxDictAll:
            if name in resultsVar.rangedFluxDict:
                rangedFluxDictAll[name].net.hi   = resultsVar.rangedFluxDict[name][1] 
                rangedFluxDictAll[name].net.lo   = resultsVar.rangedFluxDict[name][0]
                
                rangedFluxDictAll[name].forward  = 'NA'
                rangedFluxDictAll[name].backward = 'NA'
                rangedFluxDictAll[name].exchange = 'NA'

#    This screws up the ELVA!!!
#                # Normalize for 13C fluxes                
#                if name in rangedFluxDict:
#                    rangedFluxDict[name].net.hi = resultsVar.rangedFluxDict[name][1]/inFluxRef 
#                    rangedFluxDict[name].net.lo = resultsVar.rangedFluxDict[name][0]/inFluxRef
#                    
#                    rangedFluxDict[name].forward  = 'NA'
#                    rangedFluxDict[name].backward = 'NA'
#                    rangedFluxDict[name].exchange = 'NA'
                    
         
        # TODO: there is probably no reason to store this here anymore. Eliminate! Actually, leave for debugging purposes
        results.rangedFluxDictAll = rangedFluxDictAll
        results.rangedFluxDict    = rangedFluxDict
        
        # Storing result in reaction list
        results.ReacNet.C13ReacNet.reactionList.addFluxes(results.rangedFluxDict)
        results.ReacNet.reactionList.addFluxes(results.rangedFluxDictAll)             
        
        return results

    def testCoreRxns(self):
        # Test that there are core reactions included
        C13ReactionList = self.ReacNet.reactionList.getCarbonTransitionReactions(self.ReacNet.getFluxRefScale())   
        assert len(C13ReactionList.reactions) > 0, "No core reactions included"        

    def findFluxesStds(self,Nrep=20,Nrand=5,erase=True,labelMin=0.99,fluxLimit=[0,0.05,0.2],limitFlux2Core=True,maxFlux13C=[],procString='raw'):
        "Finds fluxes and standard deviations"

        # Test that there are core reactions included
        self.testCoreRxns()
        
        if limitFlux2Core:
            self.limitFlux2Core(fluxLimit)
                
        return C13Model.findFluxesStds(self,Nrep,Nrand,erase,labelMin=labelMin,maxFlux13C=maxFlux13C,procString=procString)
     
    def findFluxesRanges(self,Nrep,fluxNames,erase=True,labelMin=0.99,fluxLimit=[0,0.05,0.2],limitFlux2Core=True,maxFlux13C=[],procString='raw'):
        "Finds fluxes and ranges of fluxes within allowable Objective Function"     

        # Test that there are core reactions included
        self.testCoreRxns()    
        
        if limitFlux2Core:
            self.limitFlux2Core(fluxLimit)                                   
           
        return C13Model.findFluxesRanges(self,Nrep,fluxNames,erase,labelMin=labelMin,maxFlux13C=maxFlux13C,procString=procString)
              
    
    def limitFlux2Core(self,limits=[0,0.05]):
        "Limits flux into core metabolism to either 0 or limit input"
        FBAFile = self.ReacNet
        inFluxRef = self.ReacNet.inFluxRef
        Verbose = False
        warnFail= True if Verbose else False
        
        # Initial notes with (e.g) frag info on whether to include for fit
        initNotes    = self.ReacNet.notes
        C13initNotes = self.ReacNet.C13ReacNet.notes        
                
        # Raising error if biomass lower bound is zero, because it will create problems with SecureFluxToDest
        bmrxn = self.ReacNet.reactionList.getBiomassReaction()       
        if bmrxn.fluxBounds.net.lo <= 0:
            raise Exception('Lower bound of biomass must be bigger than zero.')
                
        # Get fluxes flowing into core metabolites
        reacsFlowingIntoCore = self.ReacNet.getReacsFlowingIntoCore()
       
        # Testing which fluxes can be set to zero        
        fluxDict       = self.ReacNet.reactionList.getFluxDictionary()
        fluxBoundsDict = self.ReacNet.reactionList.getFluxBoundsDictionary()
        FBAmod     = FBAModel(FBAFile.getSBMLString())

        if Verbose:        
            FBAFile.write('KEIOlimfileBefore.sbml')  
            print "limits:"
            print limits
        
        resultsFBA = FBAmod.findFluxes(warnFail=warnFail)
        if Verbose:
            print "successful?(limitFlux2Core before)"
            print resultsFBA.successful
        if not resultsFBA.successful:
            raise Exception('Extracellular fluxes infeasible')


        for reaction in reacsFlowingIntoCore.reactions:
            if Verbose:
                print "limiting flux to "+reaction.name
                    
            fluxBound = fluxBoundsDict[reaction.name]
            ub = fluxBound.net.hi
            lb = fluxBound.net.lo
            
            limitIter  = limits.__iter__()
            limit      = limitIter.next()
            goOn       = True
            while goOn:
                # Try setting to limit
                if reaction.hasForwardFlow:
                    fluxBound.net.hi = min(ub, abs(limit*inFluxRef)) 
                elif reaction.hasBackwardFlow:
                    fluxBound.net.lo = max(lb,-abs(limit*inFluxRef))                    
                else:
                    raise Exception("Reaction "+ reaction.name +" should not be included among those flowing into core")
            
                FBAmod.changeFluxBoundsFAST(reaction.name,fluxBound)
                FBAResults = FBAmod.findFluxes(warnFail=warnFail)                         
        
                unsuccessful = not FBAResults.successful
                
                # check if there is a next level
                isNext   = True
                limitOld = limit
                try: 
                    limit        = limitIter.next()
                except StopIteration:
                    isNext = False
                
                # Only continue if there is a next level and FBA was unsuccessful
                goOn = unsuccessful and isNext    

            if Verbose:
                print "reaction "+reaction.name+" set to level = "+str(limitOld)

            
        resultsFBA = FBAmod.findFluxes(warnFail=warnFail)
        if not resultsFBA.successful:
            raise Exception('Flux limits to core too stringent!!')
        
        if Verbose:
            print "successful?(limitFlux2Core after)"
            print resultsFBA.successful
        
        # Storing changes in ReacNet
        if Verbose:
            FBAmod.writeSBML('KEIOlimfile.sbml')
        FBAmod.recordFASTchanges()
        self.ReacNet = SBMLclasses.TSReactionNetwork(FBAmod.writeSBML('toString'))
        self.ReacNet.notes = initNotes
        self.ReacNet.C13ReacNet.notes = C13initNotes


    # External Labeling Variability Analysis (ELVA)
    def getELVAfile(self,results):
        # Function to obtain complementary reactions, sources and feeds.
        def complement13C(Smat,Fluxes,inFluxRef):
            # Find complementary reactions, sources and feeds for ELVA 
            carbonstr = 'abcdefghijklmnopqrst';
            mets = Smat.mets
            rxns = Smat.rxns
            S    = numpy.matrix(Smat.getSmatrix())
            v    = numpy.zeros((len(rxns),1))
            metList = self.ReacNet.C13ReacNet.metList
    
        
            for flux in Fluxes:
                v[rxns.index(flux)] = Fluxes[flux].net.best
              
            #   Finding metabolites involved in core reactions (and not excluded)
            metsCore = core.metList(set(self.ReacNet.C13ReacNet.metList.mets) - set(self.ReacNet.C13ReacNet.metList.getExcluded()))
            metsCoreDict = metsCore.getMetDict()
 
        
            #   Finding reactions not involved in core 
            reacsCore   = set(self.ReacNet.C13ReacNet.reactionList.getReactionNameList(level=1)) 
            
            self.ReacNet.C13ReacNet.write('C13test.sbml')
            
            indReacsCore = []
            for reac in reacsCore:
                indReacsCore.append(rxns.index(reac))
            reacsNoCore = set(rxns) - set(self.ReacNet.C13ReacNet.reactionList.getReactionNameList(level=1))            
            indReacsNoCore = []
            for reac in reacsNoCore:
                indReacsNoCore.append(rxns.index(reac))
        
            #   Finding core mets with nonzero net flux coming in
            inout    = S[:,indReacsNoCore]*v[indReacsNoCore]
            coreFlux = S[:,indReacsCore]*v[indReacsCore]
            metsNonZeroTuple   = []
            metNonZeroFluxDict = {}
            for index in range(inout.shape[0]):
                if mets[index] in metsCoreDict and inout[index]!=0:
                    metsNonZeroTuple.append((mets[index],inout[index][0,0],coreFlux[index][0,0]))
                    
                    # Extra info for report. This could be written more elegantly.
                    fluxStDictCore    = {}
                    fluxStDictNonCore = {}                    
                    for Jind in range(S.shape[1]):
                        fluxSt = S[index,Jind]*v[Jind]
                        if fluxSt !=0:
                            if rxns[Jind] in reacsCore:
                                fluxStDictCore[rxns[Jind]] = fluxSt
                            else:
                                fluxStDictNonCore[rxns[Jind]] = fluxSt
                    if fluxStDictCore or fluxStDictNonCore:
                        metNonZeroFluxDict[mets[index]] = (fluxStDictCore,fluxStDictNonCore) 


            # Initialization for report output
            report = {}
        
            #   Final packing of newmets and newreactions
            newmets      = []
            newreactions = []
            carbondict = self.ReacNet.C13ReacNet.reactionList.getCarbonDict()
            metDict    = metList.getMetDict()
            epsilon    = 0.00001

            for met,fluxinout,coreFlux in metsNonZeroTuple:
                ncarb = carbondict[met]            
                value = abs(fluxinout/inFluxRef)
                if fluxinout < 0:
                    name  = "RO" + met
                    line  = name + "\t" + met + " --> Out"+met+  "\t"  +carbonstr[0:ncarb]+" : "+carbonstr[0:ncarb]
                
                    react = core.reactant(metDict[met],1)
                    prod  = core.product(core.met('OUT'+met,ncarb),1)
                    flux  = core.flux(('NA','NA'),(core.rangedNumber(value-epsilon,value,value+epsilon),'NA')) 
                    newreactions.append(core.reaction(name,reversible=False,suggested=False,measured=False,flux='None',fluxBounds=flux,reactionLine=line,exchange=False,reactants=[react],products=[prod]))
                    newmets.append(prod)
                    report[name] = value
                else:
                    name  = "RI" + met
                    line  = name + "\t" + "OUT"+ met +" --> "+met+  "\t"  +carbonstr[0:ncarb]+" : "+carbonstr[0:ncarb]
            
                    react = core.reactant(core.met('OUT'+met,ncarb,source=True,feed='free'),1)
                    prod  = core.product(metDict[met],1)
                    flux = core.flux(('NA','NA'),(core.rangedNumber(value-epsilon,value,value+epsilon),'NA')) 
                    newreactions.append(core.reaction(name,reversible=False,suggested=False,measured=False,flux='None',fluxBounds=flux,reactionLine=line,exchange=False,reactants=[react],products=[prod]))
                    newmets.append(react)   
                    report[name] = value
        
            # Output to file
            outputFileName = 'ELVAfluxReport.txt'
            outputFile = open(outputFileName,'w')
            #outputFile.write('Y axis of ELVA plot:value, low value and high value\n')
            for name in sorted(report):
                stringOut = '{0:5.4f}'.format(report[name])
                outputFile.write(str(name)+"("+stringOut+"):\n")
                fluxStDictCore,fluxStDictNonCore = metNonZeroFluxDict[name.replace('RO','',1).replace('RI','',1)]

                outputFile.write("      ----> Non Core:\n")
                for fluxName in sorted(fluxStDictNonCore):
                    outputFile.write("      "+str(fluxName)+"   "+str(fluxStDictNonCore[fluxName])+"\n")  
    
                outputFile.write("      ----> Core:\n")
                for fluxName in sorted(fluxStDictCore):
                    outputFile.write("      "+str(fluxName)+"   "+str(fluxStDictCore[fluxName])+"\n")
  

            return newmets,newreactions
    
        
        # Find complementary reactions, sources and feeds for ELVA 
        inFluxRef = self.ReacNet.inFluxRef
        Smat = self.ReacNet.reactionList.getStoichMatrix()
        Fluxes  = results.rangedFluxDictAll 

        newmets,newreactions = complement13C(Smat,Fluxes,inFluxRef)
        
        # Old model
        oldC13Model = C13Model(self.ReacNet.C13ReacNet.getSBMLString())

        # Record fluxes and fits for fixing fluxes
        oldC13Model.recordFluxes(results.rangedFluxDict)
        oldC13Model.recordFits(results.EMUlabel)
        
        # Add new mets and reactions
        reactionList = oldC13Model.ReacNet.reactionList
        metList      = oldC13Model.ReacNet.metList
        
        newReactionsAll = copy.deepcopy(reactionList.reactions)
        newMetsAll      = copy.deepcopy(metList.mets)
        
        newReactionsAll.extend(newreactions)
        newMetsAll.extend(newmets)
        
        newReactionList = core.reactionList(newReactionsAll)
        newMetList      = core.metList(newMetsAll)
        
        # New model
        modelName  = 'ELVAmodel'
        Notes      = oldC13Model.ReacNet.notes
        # TODO: eliminate from Notes fragments not included in the fit?
                
        newReactNet = SBMLclasses.C13ReactionNetwork( (modelName,Notes,newMetList,newReactionList))
        
        return newReactNet.write('toString')
        
        
    def ELVA(self,results,erase=True,labelMin=0.99,procString='raw'):

        newSBMLFileName   = 'ELVAFileB.sbml'        
        newSBMLFileString = self.getELVAfile(results)
                
        ExpC13Model = ELVAModel(newSBMLFileString)

        ExpC13Model.ReacNet.write(newSBMLFileName)
        
        #newResults = ExpC13Model.findFluxesStds(dirFinal=os.getcwd()+'/',erase=erase,labelMin=labelMin)    
        newResults = ExpC13Model.findFluxesStds(erase=erase,labelMin=labelMin,procString=procString)    

        
        return newResults
        
    
    def addFluxes(self,fluxDictionary):
        "Adds fluxes from dictionary to all reactions lists in model"
        fluxDict = copy.deepcopy(fluxDictionary)
        #    Genome-scale
        self.ReacNet.reactionList.addFluxes2(fluxDict)
        #self.ReacNet.updateSBML()
        inFluxRef = self.ReacNet.inFluxRef 
        #    core reactions
        for name in fluxDict.keys():
            fluxDict[name] = fluxDict[name]/inFluxRef             
        self.ReacNet.C13ReacNet.reactionList.addFluxes2(fluxDict)
        self.ReacNet.C13ReacNet.reactionList.zeroFluxExchange()
        #self.ReacNet.C13ReacNet.updateSBML()   



class ELVAModel(FluxModel,C13Model):
    "Class for ELVA = External Labeling Variability Analysis calculations."
    # TODO: check the effect of fragments not to be fit
    
    def __init__(self,sbmlFileName):
        
        #TODO: recheck this class!!!!!!!
        # GAMS file name

        GAMSfileName    = "GAMS_EMU_MFA_GCMSvar.gms"
        
        # Reaction network
        ReacNet      = SBMLclasses.C13ReactionNetwork(sbmlFileName)

        # Fix fluxes    (This should be done through method in sbml class)
        #reactionList  = sbmlFile.reactionList
        reactionList  = copy.deepcopy(ReacNet.reactionList)
        
        reactionList.fixFluxes(level=2)
        
        #reactionList.fixFluxes(level=1)        
        ReacNet = SBMLclasses.C13ReactionNetwork( (ReacNet.modelName,ReacNet.notes,ReacNet.metList,reactionList))
        ReacNet.write('ELVAFile2.sbml')


        # Loading output functions
        outputFuncs = {'Info':(infoOut,['OFGenInfo.txt']),
                       'Vout':(fluxParOut,['Vout.txt','Vout']), 
                       'fout':(GAMSclasses.parOut,['fout.txt','fout']),
                       'labelcomp':(labelingParOut,['labelcomp.txt','labelcomp']),
                       #'infeasibilities':(getInfeasibilities,[infeasFileName])                           
                       'bounds':(GAMSclasses.parOut,['bounds.txt','bounds'])    
                        }
                        
        self.getFilesFunctionName    = 'get13CMFAfiles'
        self.resultsFunctionNameRand = 'ELVAResults'

        
        FluxModel.__init__(self,ReacNet,GAMSfileName,outputFuncs)
    
    def findFluxesStds(self,erase=True,labelMin=0.99,procString='raw'):
        
        results = C13Model.findFluxesStds(self,Nrep=0,Nrand=0,erase=erase,labelMin=labelMin,procString=procString)

        return results

    def getGAMSFileRand(self,maxFlux13C,maxTime=[]):
        "Returns GAMS file for the ranged fluxes approach"
        gamsFileRand  = file2tuple(self.dirGAMSFile+'GAMS_EMU_MFA_GCMSvar.gms')        
        gamsFileRand  = self.GAMSFileModifications(gamsFileRand,maxFlux13C,maxTime)      
        
        return gamsFileRand      
      
    def getOutputFuncsRand(self):
        """Returns output functions for randomization  approach"""
        
        # GAMS file name
        #GAMSfileName    = "GAMS_EMU_MFA_FLUX.gms"            # TODO: change this to a method: getGAMSFileRnd
        #GAMSfileName    = self.getGAMSFileRand([])[0]
        #infeasFileName  = GAMSfileName.replace('gms','lst')     


        # Loading output functions
        outputFuncs = {'Info':(infoOut,['OFGenInfo.txt']),
                       'Vout':(fluxParOut,['Vout.txt','Vout']), 
                       'fout':(GAMSclasses.parOut,['fout.txt','fout']),
                       'labelcomp':(labelingParOut,['labelcomp.txt','labelcomp']),
                       #'infeasibilities':(getInfeasibilities,[infeasFileName])                           
                       'bounds':(GAMSclasses.parOut,['bounds.txt','bounds'])    
                        }
                                
        return outputFuncs        
            

    def getResultsStds(self,resultsDict):
        "Produces results out of the results dictionary"        
        results     =   ELVAResults(resultsDict,self.ReacNet)           

        return results

    def createBatchRand(self,Nrep,Nrand,labelMin,maxFlux13C,erase,procString='raw'):
        # Create Batch of gams problems        
        ReacNet     = self.ReacNet
        gamsFile    = self.gamsFile
        gamsFile = self.getGAMSFileRand(maxFlux13C)
        #if maxFlux13C:         
        #    gamsFile = substituteInFile(gamsFile,[('maxflow13CU',maxFlux13C)])   
        outputFuncs = self.getOutputFuncsRand()                        
        #outputFuncs  = self.outputFuncs
        fragDict     = ReacNet.fragDict()
        # Nrep and Nrad are ignored
        
        problems = []
        for abbrev in fragDict:
            frag = fragDict[abbrev]
            for m in range(len(frag.MDV)):
                Name    = '/Run'+abbrev+'M'+str(m)
                dirName = os.getcwd()+Name
                GAMSInputFiles = self.getGAMSInputFiles(ReacNet,labelMin,procString=procString)
                
                # Add files for fragment and m to focus on
                fragFocus = GAMSclasses.GAMSset('fragfocus',set([str(frag.abbrev)]))
                nFocus    = GAMSclasses.GAMSset('nfocus',set(str(m)))
                
                fragFileName = 'fragfocus.txt'
                nFileName    = 'nfocus.txt'
                
                fragFocusSt = fragFocus.write('toString')
                nFocusSt    = nFocus.write('toString')
                
                GAMSInputFiles.extend([(fragFileName,fragFocusSt),(nFileName,nFocusSt)])
                # Writing problem
                GAMSprob       = GAMSclasses.GAMSproblem(Name,gamsFile,GAMSInputFiles,outputFuncs,directory = dirName)
                GAMSprob.erase = erase     # TODO: write as an argument in line above
                problems.append(GAMSprob)
    
        batch = GAMSclasses.GAMSproblemBatch(problems)
        batch.erase = erase     # TODO: write as an argument in line above. There should be no need to repeat this info        
        
        return batch    


# Classes for results in GAMSproblem
class Results:
    def __init__(self,resultsDict,ReacNet):
        self.ReacNet = copy.deepcopy(ReacNet)
        self.resultsDict = resultsDict
        self.fragDict = ReacNet.fragDict()
        self.processResults()
        delattr(self,'resultsDict')     # This files are big, better not to keep them
        
    
    def outputData(self,bestResults):  #TODO put this under c13 results
        # flux fit
        FITFluxes   =  bestResults[0]['Vout'].getReactionList().getFluxDictionary()
        # Std calculation
        attribs = ['forward','backward','net','exchange']
        fluxesList = []
        for randomization in bestResults:
            if randomization !=0: 
                fluxes   =  bestResults[randomization]['Vout'].getReactionList().getFluxDictionary()
                fluxesList.append(fluxes)
        fluxNames = bestResults[0]['Vout'].getReactionList().getFluxDictionary().keys()
        fluxDictEnsemble = fluxDictEns(fluxesList,fluxNames,fluxDictRef=bestResults[0]['Vout'].getReactionList().getFluxDictionary())
        FITFluxesVar     = fluxDictEnsemble.getFluxDictStd(attribs)
        FITFluxesVarHi,FITFluxesVarLo  = fluxDictEnsemble.getFluxDictStdRef(attribs)
        
        
        # Ranged fluxes calculation
        ranged = {}
        rangedFluxDict  = {}
        for flux in sorted(FITFluxesVar[attribs[0]]):
            for attrib in attribs:
#                ranged[attrib] = core.rangedNumber(getattr(FITFluxes[flux],attrib)  - FITFluxesVar[attrib][flux]/2, getattr(FITFluxes[flux],attrib) , getattr(FITFluxes[flux],attrib)  + FITFluxesVar[attrib][flux]/2)
                ranged[attrib] = core.rangedNumber(FITFluxesVarLo[attrib][flux], getattr(FITFluxes[flux],attrib) , FITFluxesVarHi[attrib][flux])
        
            rangedFlux = core.flux((ranged['forward'],ranged['backward']),(ranged['net'],ranged['exchange']))
            rangedFluxDict[flux] = rangedFlux
        
          
        # Computational labeling
        #print "labelcomp:"
        #print bestResults[0]['labelcomp']
        EMULabelDict = bestResults[0]['labelcomp'].getLabelingDict(self.fragDict)
    
        # Objective function value
        OF           = bestResults[0]['Info'].OF
        
        return rangedFluxDict,EMULabelDict,OF    
    
    def plotExpvsCompLabelXvsY(self,titleFig='',axes='default',color='b',fmt='.',save='default'):
        # TODO: move this to C13 results
        # Obtaining experimental data
        try:
            fragDict = self.fragDict
        except AttributeError:
            raise Exception('GCMS Dictionary not available')
    
        # Obtaining fit data
        EMULabelDict = self.EMUlabel
        
        # Obtaining intersection of keys
        allKeys = list(set(fragDict.keys()).intersection(set(EMULabelDict.keys())))        
        
        # Obtaining fragments not included in the fit
        nonFitKeys = []
        fitKeys    = []
        for key in allKeys:
            if fragDict[key].inFit:
                fitKeys.append(key)
            else:
                nonFitKeys.append(key)
        
        # Creating axes if needed
        if axes =='default':
            axes = figure(figsize=(8,8)).add_subplot(111)        
        axes.plot([0,1],[0,1],'k')
        axes.axis([0,1,0,1])
        
        xlabel('Experimental GCMS')
        ylabel('Computational GCMS')
    
        #XvsYcomp(fragDict,EMULabelDict,allKeys,axes,color,fmt)
        XvsYcomp(fragDict,EMULabelDict,fitKeys,axes,color,fmt)
        XvsYcomp(fragDict,EMULabelDict,nonFitKeys,axes,'g',fmt)

        
        title(titleFig,fontweight='bold')
        # Save fig        
        if save != 'default':
            savefig(save)  
        
        
    def plotExpvsCompLabelFragment(self,fragment = 'all',outputFileName='ExpvsCompLabelFragment.txt',titleFig='',save='default'):
        # TODO: move this to C13 results
        # Obtaining experimental data
        try:
            fragDict = self.fragDict
        except AttributeError:
            raise Exception('GCMS Dictionary not available')
    
        # Obtaining fit data
        EMULabelDict = self.EMUlabel

        # Adapting input
        if fragment == 'all':
            fragments = EMULabelDict.keys()
        elif isinstance(fragment,str):
            fragments = [fragment]

        # Doing plot            
        histcomp(EMULabelDict,fragDict,fragments,outputFileName,titleFig,self.OF,save)
 


    def findxyDxDy(self,fluxDictA,fluxDictB):
        "Finds values of x, y, DxU, DxL, DyU and DyL for plot"
        
        x    = []
        y    = []
        DxU  = []
        DxL  = []
        DyU  = []
        DyL  = []
        
        fluxComp = {}
        
        for flux in fluxDictA:
            if flux in fluxDictB:
                try:
                    xval  = fluxDictA[flux].net.best
                    xvalU = fluxDictA[flux].net.hi-fluxDictA[flux].net.best
                    xvalL = fluxDictA[flux].net.best-fluxDictA[flux].net.lo
                except AttributeError:
                    try:
                        xval  = fluxDictA[flux].net
                    except AttributeError:
                        xval  = fluxDictA[flux]
                    xvalU = 0
                    xvalL = 0
                    
                try:
                    yval  = fluxDictB[flux].net.best
                    yvalU = fluxDictB[flux].net.hi-fluxDictB[flux].net.best
                    yvalL = fluxDictB[flux].net.best-fluxDictB[flux].net.lo
                except AttributeError:
                    try:
                        yval  = fluxDictB[flux].net
                    except AttributeError:
                        yval  = fluxDictB[flux]
                    yvalU = 0
                    yvalL = 0
                
                
                x.append(xval)
                DxU.append(xvalU)
                DxL.append(xvalL)
                 
                y.append(yval)
                DyU.append(yvalU)
                DyL.append(yvalL)
                
                fluxComp[flux] = [xval,xval-xvalL,xval+xvalU,yval,yval-yvalL,yval+yvalU]
        
        x    = numpy.array(x)    
        dxU  = numpy.array(DxU)  
        dxL  = numpy.array(DxL)  
              
        y    = numpy.array(y)    
        dyU  = numpy.array(DyU)  
        dyL  = numpy.array(DyL)
        
        return x,dxU,dxL,y,dyU,dyL,fluxComp
      
    def createFigure(self,titleFig='',axes='default',Xlabel='External fluxes',Ylabel='Internal fluxes',xMax=2.2,yMax=2.2):
        "Creates figure"
        if axes == 'default':
            axes = figure(figsize=(8,8)).add_subplot(111)
        axes.plot([0,xMax],[0,yMax],'k')
        axes.axis([0,xMax,0,yMax])

        xlabel(Xlabel)
        ylabel(Ylabel)

        title(titleFig)     
    
        return axes
        
    
    def compareFluxes(self, FluxDict, titleFig='',outputFileName="fluxComparison.txt",axes='default',Xlabel='default',Ylabel='default',Xmax='default',Ymax='default'):        
        
        self.compareFluxesBase(self.rangedFluxDict,FluxDict,titleFig=titleFig,outputFileName=outputFileName,axes=axes,Xlabel=Xlabel,Ylabel=Ylabel,Xmax=Xmax,Ymax=Ymax)

    def compareFluxesBase(self,fluxDictA,fluxDictB,titleFig='',outputFileName="fluxComparison.txt",axes='default',Xlabel='default',Ylabel='default',Xmax='default',Ymax='default'):
        "Core function"
        
        # Obtaining x and y data
        x,dxU,dxL,y,dyU,dyL,fluxComp = self.findxyDxDy(fluxDictA,fluxDictB)

        # Plotting data
        Xmax = 1.05*max(x) if Xmax=='default' else Xmax
        Ymax = 1.05*max(x) if Ymax=='default' else Ymax
        axes = self.createFigure(titleFig=titleFig,axes=axes,Xlabel=Xlabel,Ylabel=Ylabel,xMax=Xmax,yMax=Ymax)
        axes.errorbar(x,y,yerr=[dyL,dyU],xerr=[dxL,dxU],fmt='o')

        # Output to file
        outputFile = open(outputFileName,'w')
        outputFile.write('Local fluxes (best,lo,hi), Outside fluxes (best,lo,hi):\n')
        for flux in fluxComp:
            outputFile.write(str(flux)+": "+str(fluxComp[flux])+"\n")


    def printFluxes(self,fileName='None',names='default',fluxDict='default',nonZero=False,brief=True):   # TODO call this from within reaction list
        "nonZero decides whether to print fluxes with nonzero values"
        
        if fluxDict == 'default':
            Fluxes = self.rangedFluxDict
        else:
            Fluxes = fluxDict    
            
        lines = []
        
        # Fluxes to print
        if names == 'default':
            names = Fluxes.keys()
        if names == 'exchange':
            tolerance = 0.0001
            names = []
            for name in Fluxes.keys():
                if (('EX_' in name) or ('iomass' in name)) and (abs(Fluxes[name].net.best)>tolerance) :
                    names.append(name)            
        
        # sort by quantity
        for flux in sorted(names, key=lambda name: abs(Fluxes[name].net.best),reverse=True):         
            if brief:
                lines.append(flux+": \t"+str(Fluxes[flux].net.best)+'\n')
            else:                
                lines.append(flux+':\n')
                lines.append(Fluxes[flux].__str__())
                lines.append('\n')

      
        # Output
        if fileName == 'None':    # Print to screen
            for line in lines:
               print line
        elif fileName == 'toString':  # Print to string and return
            out = ''.join(lines)
            return out             
        else:                   # Print to file
            file = open(fileName,'w')
            for line in lines:
                file.write(line)
            file.close()

    def writeSBML(self,filename):        
        doc1   = libsbml.readSBMLFromString(self.ReacNet.getSBMLString())
        libsbml.writeSBMLToFile(doc1, filename)

    def drawFluxesBase(self,normFluxDict,fileName,svgInFileName='Ecolireactionslevel_1J.svg',title='',oldVersion=False):        
        
       if not oldVersion: 
           # Only add the default path if the given path is not absolute
           if svgInFileName[:1] != '/':
               qmodeldir   = os.environ['QUANTMODELPATH']
               svgDir      = qmodeldir+'/code/visualization/fluxes/'
               svgin = svgDir+svgInFileName
           else:
                svgin = svgInFileName

           print "svgin:"
           print svgin     
        
           # instantiate FluxMap object
           fmap = FluxMap(inputFilename=svgin)
        
           # change title
           #fmap.changeTitle(title) # Deprecated

           # change all fluxes
           fmap.changeAllFluxes(normFluxDict)

           # write the svg out
           fmap.writeSVG(fileName)        
       
       else:   # TODO: deprecate this feature as soon as all maps are actualized
           
           qmodeldir   = os.environ['QUANTMODELPATH']
           svgDir      = qmodeldir+'/code/visualization/fluxes/' 

           # set parameters for flux map
           svgin=svgDir+svgInFileName
           print "svgin:"
           print svgin     
        
           # instantiate FluxMap object
           fmap = core.FluxMap(svgin)
        
           # change title
           fmap.changetitle(title)

           # change all fluxes
           fmap.changeallfluxes(normFluxDict)

           # write the svg out
           fmap.writesvg(fileName)    
        
        
    def drawFluxes(self,fileName,svgInFileName='Ecolireactionslevel_1J.svg',norm='',titleTag=' (13C FVA)',oldVersion=False):        
        # Initial input
        #rangedFluxDict = self.rangedFluxDict
    
        # Normalizing Flux dictionary
        #self.ReacNet.reactionList.addFluxes(rangedFluxDict)
        norm = self.ReacNet.getHighestCarbonInput() if not norm else norm  
        
        normFluxDict = copy.deepcopy(self.ReacNet.reactionList.getFluxDictionary(level=1,fluxComp='net',rangeComp='all',norm=norm))
  
        # Passing it to base function
        title = self.ReacNet.modelName+self.titleTag
        self.drawFluxesBase(normFluxDict,fileName,svgInFileName=svgInFileName,title=title,oldVersion=oldVersion)        
  
      
    def saveFluxLims2Bounds(self):
        # sets the fluxes upper and lower values to bounds in sbml file
        ReacNet = self.ReacNet
        rangedFluxDict = self.rangedFluxDict
        metList      = ReacNet.metList
        reactionList = ReacNet.reactionList

        for reaction in reactionList:
            if reaction.name in rangedFluxDict:
                reaction.fluxBounds.net.hi = rangedFluxDict[reaction.name].net.hi  
                reaction.fluxBounds.net.lo = rangedFluxDict[reaction.name].net.lo                  

        # Store everything back into sbml (unnecessary now)
        #ReacNet.sbmlFileString = ReacNet.getSBMLFromTuple( (ReacNet.modelName,ReacNet.notes,metList,reactionList) )            

    def saveFluxVal2Bounds(self):
        # sets the flux values to bounds in sbml file
        ReacNet = self.ReacNet
        rangedFluxDict = self.rangedFluxDict
        metList      = ReacNet.metList
        reactionList = ReacNet.reactionList

        for reaction in reactionList:
            if reaction.name in rangedFluxDict:
                reaction.fluxBounds.net.hi = rangedFluxDict[reaction.name].net.best  
                reaction.fluxBounds.net.lo = rangedFluxDict[reaction.name].net.best                  

        # Store everything back into sbml
        #ReacNet.sbmlFileString = ReacNet.getSBMLFromTuple( (ReacNet.modelName,ReacNet.notes,metList,reactionList) )   

    def plotMetaboliteFlux(self,metName, minFluxGroup = 0.05, maxFluxGroup=1.5,titleFig='',save='default'):
        "Sankey plot for fluxes producing and consuming a metabolite. minFluxGroup is the minimum amount of flux so it does not get grouped with others."
        
        # Fluxes for genome-scale model
        try:
            fluxes  = self.rangedFluxDictAll
        except:
            fluxes  = self.rangedFluxDict            
        
        minFlux = 0.00004     # minimum flux to be considered
        
        
        # Stoichiometry matrix
        Smat = self.ReacNet.reactionList.getStoichMatrix()
        mets    = Smat.mets
        rxns    = Smat.rxns
        S    = Smat.getSmatrix()
        
        # flows and labels
        flows   = []
        labels  = []
        #tempflux = 0
        #temprxns = ''
        units = []
        imet = mets.index(metName)             
        newFluxes = {}
        for rxn in rxns:
             jrxn = rxns.index(rxn)   
                     
             if S[imet][jrxn] != 0 and fluxes[rxn].net.best != 0:      
                #flows.append(round(fluxes[rxn].net.best*S[imet][jrxn],2))
                #stringOut = rxn+": "+str(round(fluxes[rxn].net.lo*S[imet][jrxn],2))+" - "+str(round(fluxes[rxn].net.hi*S[imet][jrxn],2))
                flows.append(round(fluxes[rxn].net.best*S[imet][jrxn],2))
                stringOut = rxn       
                labels.append(stringOut)
                newFluxes[rxn] = S[imet][jrxn]*fluxes[rxn]
                units.append((newFluxes[rxn].net,rxn))
                

       
#        flows.append(round(tempflux,2))
#        labels.append(temprxns)        
        
        # Group flow and labels
        groups = []
        groupPlus  = (core.rangedNumber(0,0,0),'')
        groupMinus = (core.rangedNumber(0,0,0),'')
        for unit in units:
            flux,label = unit
            if abs(flux.best) >= minFluxGroup:
                groups.append(unit)
            else:
                if flux.best >= 0:
                    gPflux,gPlabel = groupPlus
                    gPflux  = gPflux + flux
                    gPlabel = gPlabel+'\n'+label if gPlabel!='' else label
                    groupPlus = (gPflux,gPlabel)
                    if abs(gPflux.best) >= maxFluxGroup:
                        groups.append((gPflux,gPlabel))
                        groupPlus  = (core.rangedNumber(0,0,0),'')
                else:
                    gMflux,gMlabel = groupMinus
                    gMflux  = gMflux + flux
                    gMlabel = gMlabel+'\n'+label if gMlabel!='' else label
                    groupMinus = (gMflux,gMlabel)
                    if abs(gMflux.best) >= maxFluxGroup:
                        groups.append((gMflux,gMlabel))
                        groupMinus  = (core.rangedNumber(0,0,0),'')
        # Take care of last group
        if abs(groupPlus[0].best) < maxFluxGroup and groupPlus[1]!='':
            groups.append((gPflux,gPlabel))
        if abs(groupMinus[0].best) < maxFluxGroup and groupMinus[1]!='':
            groups.append((gMflux,gMlabel))
           
        newFlows  = []
        newLabels = []
        for group in groups:
            flux,label = group
            newFlows.append(round(flux.best,2))
            if flux.best >= 0:
                newLabels.append(label+'\n'+'['+str(round(abs(flux.lo),2))+" - "+str(round(abs(flux.hi),2))+']')
            else:
                newLabels.append(label+'\n'+'['+str(round(abs(flux.hi),2))+" - "+str(round(abs(flux.lo),2))+']')
          
        
        
        # pathlengths 
        pathlengths = []        
        for i in range(len(newLabels)):
             pathlengths.append(0.25)
        
        
        
        # orientations
        orientations = []
        
        for i in range(len(newLabels)):
            if i < (len(newLabels))/2:
                 orientations.append(-1)
            else:
                  orientations.append(1)
                  
        maxvalue = newFlows.index(max(newFlows))
        minvalue = newFlows.index(min(newFlows))
        orientations[maxvalue] = 0
        orientations[minvalue] = 0
        patchlabel = metName[0:-2].upper()
        
        
        
        # Sankey plot
        from matplotlib.sankey import Sankey
        matplotlib.rcParams.update({'font.size': 12})

        #fig = figure()    
        fig = figure(figsize=(18,18))
        title = patchlabel+" balances "+titleFig
        #if titleFig != '':
        #    title = title+'('+strain+')'
        ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],title=title)   
        sankey = Sankey(ax=ax, scale=0.15, offset=0.12)
        sankey.add(       
                   labels=newLabels,
                   flows=newFlows,
                   orientations = orientations,
                   pathlengths = pathlengths,
                   patchlabel=patchlabel,
                   alpha=0.2, lw=2.0)    # Arguments to matplotlib.patches.PathPatch()
        
        diagrams = sankey.finish()
        diagrams[0].patch.set_facecolor('b')
        diagrams[0].text.set_fontweight('bold')
        diagrams[0].text.set_fontsize(25)

        #for i in range(len(diagrams)[1:]):
        #    diagrams[i].text.set_fontsize(16)
        
        matplotlib.rcParams.update({'font.size': 20})

        # Save fig        
        if save != 'default':
            savefig(save) 


class FBAResults(Results):
    def __init__(self,resultsDict,ReacNet):
        self.ReacNet = copy.deepcopy(ReacNet)
        self.resultsDict = resultsDict
        self.rangedFluxDict = resultsDict   # This should be compacted with the previous line
        self.processResults()
        self.titleTag = ' (FBA)'  
        delattr(self,'resultsDict')     # This files are big, better not to keep them
        delattr(self,'rangedFluxDict')

        
    def processResults(self):
        Vout             = self.resultsDict['Vout']
        self.VFBA        = fluxGAMSpar(Vout.name,Vout.elements)
        self.successful  = self.resultsDict['Successful']
        
        # Ranged flux dict (PROVISIONAL: it should be changed)  
        # TODO: this should be part of its own outputData() method
        fluxDict = self.VFBA.getReactionList().getFluxDictionary()
        rangedFluxDict = {}
        for name in fluxDict:
            flux = fluxDict[name]
            rangedForw = core.rangedNumber(flux.forward ,flux.forward ,flux.forward) 
            rangedBack = core.rangedNumber(flux.backward,flux.backward,flux.backward) 
            rangedNet  = core.rangedNumber(flux.net     ,flux.net     ,flux.net) 
            rangedExch = core.rangedNumber(flux.exchange,flux.exchange,flux.exchange) 
            
            rangedFlux = core.flux((rangedForw,rangedBack),(rangedNet,rangedExch))
        
            rangedFluxDict[name] = rangedFlux
        
        self.rangedFluxDict = rangedFluxDict
        self.ReacNet.reactionList.addFluxes2(fluxDict)
        
    def printSuccess(self,onlyFail=True):
        string =  ' successful'
        if not self.successful:
            string = ' NOT'+string
        string = 'lp'+string
        
        # Print only if asked
        if onlyFail:
            if not self.successful:
                print string
        else:
            print string

class FVAResults(FBAResults):
    
    def __init__(self,resultsDict,ReacNet):
        FBAResults.__init__(self,resultsDict,ReacNet)
        self.titleTag = ' (FVA)'   
    
    def compareFluxes(self, FluxDict, titleFig='',outputFileName="fluxComparison.txt",axes='default',Xlabel='default',Ylabel='default',Xmax='default',Ymax='default'):        
        
        self.compareFluxesBase(self.resultsDict,FluxDict,titleFig=titleFig,outputFileName=outputFileName,axes=axes,Xlabel=Xlabel,Ylabel=Ylabel,Xmax=Xmax,Ymax=Ymax)

    def processResultsOUT(self):
        self.ReacNet.reactionList.addFluxes2(self.rangedFluxDict)

    def processResults(self):
        
        resultsDict = self.resultsDict

        # Output parsing
        VFBAOut    = resultsDict['Vout']
        VFBAOutMax = resultsDict['Vmax']
        VFBAOutMin = resultsDict['Vmin']
        
        VFBA    = fluxGAMSpar(VFBAOut.name,VFBAOut.elements).getReactionList().getFluxDictionary()
        VFBAmax = fluxGAMSpar(VFBAOutMax.name,VFBAOutMax.elements).getReactionList().getFluxDictionary()
        VFBAmin = fluxGAMSpar(VFBAOutMin.name,VFBAOutMin.elements).getReactionList().getFluxDictionary()
        
        # Ranged fluxes calculation
        attribs = ['forward','backward','net','exchange']
        ranged = {}
        rangedFluxDict  = {}
        for flux in VFBAmax:
            for attrib in attribs:
                ranged[attrib] = core.rangedNumber(getattr(VFBAmin[flux],attrib),getattr(VFBA[flux],attrib),getattr(VFBAmax[flux],attrib))
            rangedFluxDict[flux] = core.flux((ranged['forward'],ranged['backward']),(ranged['net'],ranged['exchange']))
            
        self.ReacNet.reactionList.addFluxes2(rangedFluxDict)
        
        self.rangedFluxDict = rangedFluxDict  

class C13Results(Results):      
    
    def __init__(self,resultsDict,ReacNet):
        Results.__init__(self,resultsDict,ReacNet)
        self.titleTag = ' (13C)'    
    
    def processResults(self):
        # Find lowest OFs for each randomization
        bestResults,bestOFs = self.findLowestOF()
        
        # Output data
        rangedFluxDict,EMUlabel,OF  = self.outputData(bestResults)
        
        # Storing result in reaction list
        #if hasattr(self.ReacNet,'C13ReacNet'):
        #    reactionList = self.ReacNet.C13ReacNet.reactionList
        #else:
        #    reactionList = self.ReacNet.reactionList        
        #reactionList.addFluxes(rangedFluxDict)  
        
        self.rangedFluxDict = rangedFluxDict
        self.EMUlabel       = EMUlabel
        self.OF             = OF
    
    def findLowestOF(self):
        # Find lowest objective functions which are feasible
        resultsDict = self.resultsDict
        bestResults = {}
        bestOFs     = {}
        infeasAll   = {}
        for name in resultsDict:
            result = resultsDict[name]
            randomization  = float(name.lstrip('/Run').split('_')[0])
            OF             = result['Info'].OF
            solvestat      = result['Info'].solvestat
            modelstat      = result['Info'].modelstat
            infeasAll[randomization] = result['infeasibilities']
            if solvestat == 1 and (modelstat == 1 or modelstat== 2):
                if randomization not in bestOFs:
                    bestOFs[randomization]     = OF
                    bestResults[randomization] = result
                else:
                    if OF < bestOFs[randomization]:
                        bestOFs[randomization] = OF
                        bestResults[randomization] = result
        
        # Should find a better way to handle this exception
        if not bestOFs:  # No feasible solutions
            print "NO FEASIBLE SOLUTIONS!!!"
            for line in infeasAll[randomization]:
                print line

            raise Exception('NO FEASIBLE SOLUTIONS!!!')            
            
            
        return bestResults,bestOFs
        
    def plotMetaboliteFlux(self,metName, minFluxGroup = 0.05, maxFluxGroup=1.5,titleFig='',save='default'):        
        print "Method not available"


class TSResults(C13Results):
    def __init__(self,resultsDict,ReacNet):
        self.ReacNet = copy.deepcopy(ReacNet)
        self.fragDict = self.ReacNet.C13ReacNet.fragDict()
        self.resultsDict = resultsDict   
        self.processResults()
        self.titleTag = ' (2S)'    
        delattr(self,'resultsDict')     # This files are big, better not to keep them

    
    def processResults(self):
        bestResults,bestOFs = self.findLowestOF()
        rangedFluxDictAll,rangedFluxDictCore,EMUlabel,OF,fluxDictEnsemble  = self.outputData(bestResults)
        
        # Add fluxes to reaction list        
        
        self.rangedFluxDict     = rangedFluxDictCore
        self.rangedFluxDictAll  = rangedFluxDictAll
        self.EMUlabel           = EMUlabel
        self.OF                 = OF
        self.fluxDictEnsemble   = fluxDictEnsemble
        
            
    def outputData(self,bestResults):
        # 13C part
        rangedFluxDict13C,EMUlabel,OF = C13Results.outputData(self,bestResults)
        # Genome-scale part (repeated code, it should be improved)
        FITFluxes   =  bestResults[0]['VFBAout'].getReactionList().getFluxDictionary()
        #     Std calculation
        attribs = ['forward','backward','net','exchange']
        fluxesList = []
        for randomization in bestResults:          
            if randomization !=0: 
                fluxes   =  bestResults[randomization]['VFBAout'].getReactionList().getFluxDictionary()
                fluxesList.append(fluxes)
        fluxNames = bestResults[0]['VFBAout'].getReactionList().getFluxDictionary().keys()
        fluxDictEnsemble = fluxDictEns(fluxesList,fluxNames,fluxDictRef=bestResults[0]['VFBAout'].getReactionList().getFluxDictionary())
        FITFluxesVar     = fluxDictEnsemble.getFluxDictStd(attribs)
        FITFluxesVarHi,FITFluxesVarLo  = fluxDictEnsemble.getFluxDictStdRef(attribs)
        
        
        #     Ranged fluxes calculation
        ranged = {}
        rangedFluxDict  = {}
        for flux in sorted(FITFluxesVar[attribs[0]]):
            for attrib in attribs:
#                ranged[attrib] = core.rangedNumber(getattr(FITFluxes[flux],attrib)  - FITFluxesVar[attrib][flux]/2, getattr(FITFluxes[flux],attrib) , getattr(FITFluxes[flux],attrib)  + FITFluxesVar[attrib][flux]/2)        
                ranged[attrib] = core.rangedNumber(FITFluxesVarLo[attrib][flux], getattr(FITFluxes[flux],attrib) , FITFluxesVarHi[attrib][flux])
        
            rangedFlux = core.flux((ranged['forward'],ranged['backward']),(ranged['net'],ranged['exchange']))
            rangedFluxDict[flux] = rangedFlux
        
        return rangedFluxDict,rangedFluxDict13C,EMUlabel,OF,fluxDictEnsemble

    def compareFluxesCore(self,FluxDict,titleFig='',outputFileName="fluxComparisonCore.txt",axes='default'):
        # Using function from C13
        C13Results.compareFluxes(self,FluxDict, titleFig = titleFig, outputFileName = outputFileName, axes = axes)
    
#    def compareFluxesAll(self, FluxDict, titleFig='',outputFileName="fluxComparisonAll.txt",axes='default',Xlabel='default',Ylabel='default'):        
#
#        # Obtaining x and y data
#        x,dxU,dxL,y,dyU,dyL,fluxComp = self.findxyDxDy(self.rangedFluxDictAll,FluxDict)
#
#        # Plotting data
#        axes = self.createFigure(titleFig=titleFig,axes=axes,Xlabel=Xlabel,Ylabel=Ylabel,xMax=1.05*max(x),yMax=1.05*max(y))
#        axes.errorbar(x,y,yerr=[dyL,dyU],xerr=[dxL,dxU],fmt='o')
#
#        # Output to file
#        outputFile = open(outputFileName,'w')
#        outputFile.write('Outside fluxes, local fluxes, local fluxes var:\n')
#        for flux in fluxComp:
#            outputFile.write(str(flux)+": "+str(fluxComp[flux])+"\n")

    def compareFluxesAll(self, FluxDict, titleFig='',outputFileName="fluxComparisonAll.txt",axes='default',Xlabel='default',Ylabel='default',Xmax='default',Ymax='default'):        
        
        self.compareFluxesBase(self.rangedFluxDictAll,FluxDict,titleFig=titleFig,outputFileName=outputFileName,axes=axes,Xlabel=Xlabel,Ylabel=Ylabel,Xmax=Xmax,Ymax=Ymax)


    def printFluxesAll(self,fileName='None',names='default'):
        return self.printFluxes(fileName,names,fluxDict = self.rangedFluxDictAll)

# Classes for results in ELVA       
class ELVAResults(Results):
        
    def processResults(self):
        labelMinMax = self.outputData()
        
        self.labelMinMax = labelMinMax
        
    def outputData(self):
        labelMinMax = {}
        resultsDict = self.resultsDict
        regex       = re.compile('([\w\-]+)(M\d+)')
        
        for dirName in resultsDict:
            result = resultsDict[dirName]
            matches = regex.match(dirName.lstrip('/Run'))
            abbrev = matches.group(1)
            mVal   = matches.group(2).lstrip('M')
            if not abbrev in labelMinMax:
                labelMinMax[abbrev]= {}
            labelMinMax[abbrev][mVal]=[result['bounds'].elements[('min',)],result['bounds'].elements[('max',)]]
        
        return labelMinMax
        
    def getxDXyDyInfo(self):
        "Produces plotting info for plotExpvsCompLabelxvsy method"
        
        # Obtaining experimental data
        try:
            fragDict = self.fragDict
        except AttributeError:
            raise Exception('GCMS Dictionary not available')
    
        # Obtaining fit data
        labelMinMax = self.labelMinMax
        
        # Obtaining plot data
        x  = []  # Computational data (labelMinMax)
        Dx = []
        y  = []  # Experimental data (fragDict)  
        DyU= []
        DyL= []
    
        # File output lines initialization
        labelComp     = {}
        labelCompDict = {}
    
    
        # Getting data for comparison
        for abbrev in labelMinMax:
            if abbrev in fragDict:
                frag = fragDict[abbrev]
                MDV    = frag.MDV
                MDVfit = frag.MDVfit
                std  = frag.std
                
                #print "===>  abbrev: "+abbrev
                
                for m in range(min(len(MDV),len(MDVfit))):
                    x.append(MDV[m])
                    Dx.append(std[m]/2)
                    y.append(MDVfit[m])
                    DyU.append( (labelMinMax[abbrev][str(m)][1]-MDVfit[m]))
                    DyL.append(-(labelMinMax[abbrev][str(m)][0]-MDVfit[m]))
                    #print "y,Dys: "+str(MDVfit[m])+" ; "+str(labelMinMax[abbrev][str(m)][1]-MDVfit[m])+" , "+str(-(labelMinMax[abbrev][str(m)][0]-MDVfit[m]))
                    labelComp[abbrev+'M'+str(m)] = str(MDVfit[m])+' '+str(labelMinMax[abbrev][str(m)][0])+'-'+str(labelMinMax[abbrev][str(m)][1])+'---->'+str(labelMinMax[abbrev][str(m)][1]-labelMinMax[abbrev][str(m)][0])
                    labelCompDict[abbrev+'M'+str(m)] = ( MDVfit[m], labelMinMax[abbrev][str(m)][0], labelMinMax[abbrev][str(m)][1] )
    
        # Plotting
        x = numpy.array(x)
        Dx= numpy.array(Dx)
        y = numpy.array(y)
        DyU= numpy.array(DyU)
        DyL= numpy.array(DyL)
        
        return x,Dx,y,DyU,DyL,labelComp,labelCompDict
        
        
    def plotExpvsCompLabelxvsy(self,titleFig='',axes='default',outputFileName="ELVAComparison.txt",save='default'):

#        # Obtaining experimental data
#        try:
#            fragDict = self.fragDict
#        except AttributeError:
#            raise Exception('GCMS Dictionary not available')
#    
#        # Obtaining fit data
#        labelMinMax = self.labelMinMax
#        
#        # Obtaining plot data
#        x  = []  # Computational data (labelMinMax)
#        Dx = []
#        y  = []  # Experimental data (fragDict)  
#        DyU= []
#        DyL= []
#    
#        # File output lines initialization
#        labelComp = {}
#    
#        # Getting data for comparison
#        for abbrev in labelMinMax:
#            if abbrev in fragDict:
#                frag = fragDict[abbrev]
#                MDV    = frag.MDV
#                MDVfit = frag.MDVfit
#                std  = frag.std
#                
#                #print "===>  abbrev: "+abbrev
#                
#                for m in range(min(len(MDV),len(MDVfit))):
#                    x.append(MDV[m])
#                    Dx.append(std[m]/2)
#                    y.append(MDVfit[m])
#                    DyU.append( (labelMinMax[abbrev][str(m)][1]-MDVfit[m]))
#                    DyL.append(-(labelMinMax[abbrev][str(m)][0]-MDVfit[m]))
#                    #print "y,Dys: "+str(MDVfit[m])+" ; "+str(labelMinMax[abbrev][str(m)][1]-MDVfit[m])+" , "+str(-(labelMinMax[abbrev][str(m)][0]-MDVfit[m]))
#                    labelComp[abbrev+'M'+str(m)] = str(MDVfit[m])+' '+str(labelMinMax[abbrev][str(m)][0])+'-'+str(labelMinMax[abbrev][str(m)][1])+'---->'+str(labelMinMax[abbrev][str(m)][1]-labelMinMax[abbrev][str(m)][0])
#    
#        # Plotting
#        x = numpy.array(x)
#        Dx= numpy.array(Dx)
#        y = numpy.array(y)
#        DyU= numpy.array(DyU)
#        DyL= numpy.array(DyL)        
        
        x,Dx,y,DyU,DyL,labelComp,labelCompDict = self.getxDXyDyInfo()
        
        if axes =='default':
            axes = figure(figsize=(8,8)).add_subplot(111)
        if (len(x)!=0) and (len(y)!=0):
            axes.errorbar(x,y,yerr=[DyL,DyU],xerr=[Dx,Dx],fmt='ko')    
            axes.plot([0,1],[0,1],'k')
            axes.axis([0,1,0,1])
            
            xlabel('Experimental Labeling')
            ylabel('Computational Labeling')
    
            title(titleFig,fontweight='bold')
        else:
            print "No data in plot"
            print x
            print y

        # Output to file
        outputFile = open(outputFileName,'w')
        outputFile.write('Y axis of ELVA plot:value, low value and high value\n')
        for name in sorted(labelComp):
            outputFile.write(str(name)+": "+str(labelComp[name])+"\n")

        # Save fig        
        if save != 'default':
            savefig(save)  
        

    def printLabeling(self,fileName='None',names='default'):
        labelMinMax = self.labelMinMax
        
        lines = []
        
        # Metabolites to print
        if names == 'default':
            names = labelMinMax.keys()
        
        
        for fragment in names:
            lines.append(fragment+':\n')
            lines.append(labelMinMax[fragment].__str__())
 #           for mVal in labelMinMax[fragment]:
 #               if labelMinMax[fragment][mVal][0]>labelMinMax[fragment][mVal][1]:
 #                   lines.append('!!!--> ['+str(labelMinMax[fragment][mVal][0])+','+str(labelMinMax[fragment][mVal][1])+']')
            lines.append('\n')
        
        # Output
        if fileName == 'None':    # Print to screen
            for line in lines:
               print line
        elif fileName == 'toString':
            return ''.join(lines)
        else:                   # Print to file
            file = open(fileName,'w')
            for line in lines:
                file.write(line)
            file.close()        
    
    
class C13FVAResults(Results):
    
    def __init__(self,resultsDict,ReacNet):
        self.ReacNet = copy.deepcopy(ReacNet)
        self.resultsDict = resultsDict
        self.fragDict = ReacNet.fragDict()
        self.processResults()
        self.titleTag = ' (13C FVA)'    
        delattr(self,'resultsDict')     # This files are big, better not to keep them

    
    def processResults(self):
        # Barebones, we probably need to output OF and EMUlabel (from SUGGESTED SOLUTION) as well.
        rangedFluxDict = self.outputData(self.resultsDict)
    
        self.rangedFluxDict = rangedFluxDict    
        
    def outputData(self,resultsDict):
                
        # Ranged fluxes dictionary
        rangedFluxDict = {}
        for name in resultsDict:
            result = resultsDict[name]
            topVal    = result['fluxBounds'].elements[('max',)]
            bottomVal = result['fluxBounds'].elements[('min',)]
            rangedFluxDict[name.replace('/Run_','',1)] = (bottomVal,topVal)
            
        return rangedFluxDict    
    
class TSFVAResults(C13FVAResults,TSResults):

    def __init__(self,resultsDict,ReacNet):
        TSResults.__init__(self,resultsDict,ReacNet)
        self.titleTag = ' (TS FVA)'
    
    def outputData(self,resultsDict):
        
        # Ranged fluxes dictionary
        rangedFluxDict = {}
        for name in resultsDict:
            result = resultsDict[name]
            topVal    = result['fluxBounds'].elements[('max',)]
            bottomVal = result['fluxBounds'].elements[('min',)]
            
            fluxName    = name.replace('/Run_','',1)
            fluxNameNew = fluxName            
            
            rangedFluxDict[fluxNameNew] = (bottomVal,topVal)

        
        # Debug
        debug = False
        if debug:      
            print "in debug"
            fluxName = 'G6PDH2r'
            dir ='/scratch/hgmartin_gams_files/tests/batch/bigtestp02/'
            
            # max
            result = resultsDict['/Run_'+fluxName] 
            rangedFluxDictAll = result['VFBAmaxout'].getReactionList().getFluxDictionary(level=1,fluxComp='net',rangeComp='all',norm=self.ReacNet.getHighestCarbonInput())
            #rangedFluxDictAll = result['VFBAmaxout'].getReactionList().getFluxDictionary(level=1,fluxComp='net',rangeComp='all',norm='GLCpts')
            #rangedFluxDictAll = result['VFBAmaxout'].getReactionList().getFluxDictionary(level=1,fluxComp='all',rangeComp='all',norm='GLCpts')
            self.drawFluxesBase(rangedFluxDictAll,dir+fluxName+'Maxtest.svg',svgInFileName='KEIO3.svg')
            
            self.fragDict = self.ReacNet.C13ReacNet.fragDict()
            self.EMUlabel = result['labelcompMax'].getLabelingDict(self.fragDict)
            self.OF       = result['InfoMax'].OF

            self.plotExpvsCompLabelFragment(titleFig='Max')
            
            # min
            result = resultsDict['/Run_'+fluxName]
            rangedFluxDictAll = result['VFBAminout'].getReactionList().getFluxDictionary(level=1,fluxComp='net',rangeComp='all',norm=self.ReacNet.getHighestCarbonInput())
            #rangedFluxDictAll = result['VFBAminout'].getReactionList().getFluxDictionary(level=1,fluxComp='net',rangeComp='all',norm='GLCpts')
            #rangedFluxDictAll = result['VFBAminout'].getReactionList().getFluxDictionary(level=1,fluxComp='all',rangeComp='all',norm='GLCpts')
            self.drawFluxesBase(rangedFluxDictAll,dir+fluxName+'Mintest.svg',svgInFileName='KEIO3.svg')
            
            self.fragDict = self.ReacNet.C13ReacNet.fragDict()
            self.EMUlabel = result['labelcompMin'].getLabelingDict(self.fragDict)
            self.OF       = result['InfoMin'].OF

            self.plotExpvsCompLabelFragment(titleFig='Min')
            
        return rangedFluxDict
      
    
    
# Flux GAMS parameter class (only adds an output method)
class fluxGAMSpar(GAMSclasses.GAMSpar):
    
    def __init__(self,name,elements,reactionList='default',fluxDict='default'):
        
        if reactionList != 'default':
            # if reactionList present, use that to initalize parameter elements
            elements = {}
            for reaction in reactionList:
                if reaction.reversible and not reaction.exchange:
                    elements[reaction.name+'_f'] = reaction.flux.forward.best
                    elements[reaction.name+'_b'] = reaction.flux.backward.best                        
                else:
                    elements[reaction.name] = reaction.flux.net.best
        elif fluxDict != 'default':
            elements = {}
            for fluxName in fluxDict:
                try:
                    elements[fluxName] = fluxDict[fluxName].net.best      # This should be generalized
                except AttributeError:
                    try:
                        elements[fluxName] = fluxDict[fluxName].net      
                    except AttributeError:
                            elements[fluxName] = fluxDict[fluxName]                                 
        
        GAMSclasses.GAMSpar.__init__(self,name,elements)
        
    
    def getReactionList(self):
        reactions = []
        for rxnTup in self.elements:
            name    = rxnTup[0]
            forward = self.elements[rxnTup]
            # Find if it is reversible
            if name[-2:]!='_b':
                if name[-2:]=='_f':
                    # Find backward reaction
                    name = name[0:-2]
                    backward = self.elements[tuple([name+'_b'])]
                    rev = True
                else:
                    backward = 0
                    rev = False
                flux = core.flux(for_back_tup=(forward,backward))
                reaction = core.reaction(name,reversible=rev,flux=flux)
                reactions.append(reaction)
                
        return core.reactionList(reactions)

    def compare(self,fluxDict):
        pass
        

class labelingGAMSpar(GAMSclasses.GAMSpar):
    "GAMS parameter for labeling"
    
    def getLabelingDict(self,fragDict):
        EMUlabel = self.elements
        EMULabelDict = {}
        maxLength    = {}
        # Gathering data
        for tup in EMUlabel:
            emu = tup[0]
            m   = int(tup[1])
            frag= fragDict[emu]
            nmeas = frag.nmeas
            if m <= nmeas-1:
                if emu not in EMULabelDict:
                    EMULabelDict[emu] = []
                    maxLength[emu] = 0
                EMULabelDict[emu].append((m,EMUlabel[tup]))
                maxLength[emu] = max(maxLength[emu],m)
       
        # Reordering data
        for emu in EMULabelDict:
            old = EMULabelDict[emu]
            EMULabelDict[emu] = numpy.zeros(maxLength[emu]+1)
            for tuple in old:
                m   = tuple[0]
                val = tuple[1]
                EMULabelDict[emu][m] = val
        
        return EMULabelDict
        

# Class for info in GAMSproblem
class Info:
    def __init__(self,OF,solvestat,modelstat,numequ,numnz,numvar,resusd):
        self.OF        = OF
        self.solvestat = solvestat
        self.modelstat = modelstat
        self.numequ    = numequ
        self.numnz     = numnz
        self.numvar    = numvar
        self.resusd    = resusd
        
# Class for ensemble of flux dictionaries
class fluxDictEns():
    def __init__(self,fluxDictList,fluxNames,fluxDictRef=[]):
        self.fluxDictList = fluxDictList
        self.fluxNames    = fluxNames
        self.fluxDictRef  = fluxDictRef
    # Gets dictionary of ranged fluxes
    # attribs is the attributes to average over (e.g. 'forward','backward', 'net', 'exchange')
    def getFluxDictStd(self,attribs):
        # Std calculation
        fluxDictList = self.fluxDictList 
        
        # Initialization
        FluxesDictVar = {}
        for attrib in attribs:
            FluxesDictVar[attrib] = {}
            for flux in self.fluxNames:
                FluxesDictVar[attrib][flux] = []
        if fluxDictList:        
            # Getting all attribute values into a single list
            for fluxDict in fluxDictList:
                for flux in fluxDict:
                    for attrib in attribs:
                        FluxesDictVar[attrib][flux].append(getattr(fluxDict[flux],attrib))
            # Finding std for whole list
            for attrib in attribs:
                for flux in FluxesDictVar[attrib]:
                    FluxesDictVar[attrib][flux] = numpy.std(FluxesDictVar[attrib][flux])        
        else:
            for attrib in attribs:
                for flux in FluxesDictVar[attrib]:
                    FluxesDictVar[attrib][flux] = 0  

        return FluxesDictVar
       
    def getFluxDictStdRef(self,attribs):
        "Getting mean deviations from above and below reference"
        fluxDictList = self.fluxDictList 
        fluxDictRef  = self.fluxDictRef

        # Initialization
        FluxesDictVarHi = {}
        FluxesDictVarLo = {}
        FluxesDictRef   = {}
        for attrib in attribs:
            FluxesDictVarHi[attrib]  = {}
            FluxesDictVarLo[attrib]  = {}
            FluxesDictRef[attrib] = {}
            for flux in self.fluxNames:
                FluxesDictVarHi[attrib][flux] = []
                FluxesDictVarLo[attrib][flux] = []
                FluxesDictRef[attrib][flux] = getattr(fluxDictRef[flux],attrib)
        if fluxDictRef:
            if fluxDictList:    
                # Getting all attribute values into a single list
                for fluxDict in fluxDictList:
                    for flux in fluxDict:
                        for attrib in attribs:
                            value    = getattr(fluxDict[flux],attrib)
                            valueRef = getattr(fluxDictRef[flux],attrib)
                            if value > valueRef:
                                FluxesDictVarHi[attrib][flux].append(value)                                
                            elif value < valueRef:
                                FluxesDictVarLo[attrib][flux].append(value)    
                    
                # Finding std for whole list
                for attrib in attribs:
                    for flux in FluxesDictVarHi[attrib]:
                        if not FluxesDictVarHi[attrib][flux]:
                            FluxesDictVarHi[attrib][flux] = [getattr(fluxDictRef[flux],attrib)]
                        if not FluxesDictVarLo[attrib][flux]:
                            FluxesDictVarLo[attrib][flux] = [getattr(fluxDictRef[flux],attrib)]
                        FluxesDictVarHi[attrib][flux] = numpy.mean(FluxesDictVarHi[attrib][flux])   
                        FluxesDictVarLo[attrib][flux] = numpy.mean(FluxesDictVarLo[attrib][flux])                           
            else:
                for attrib in attribs:
                    for flux in FluxesDictVarHi[attrib]:
                        FluxesDictVarHi[attrib][flux] = 0  
                        FluxesDictVarLo[attrib][flux] = 0  
        else:
            raise Exception('Flux reference not available.')

        return FluxesDictVarHi,FluxesDictVarLo
        


# Function that provides info for results from 13C flux fit GAMS problem
def infoOut(input):
    filename = input[0]
    try:
        fileInfo = open(filename)
    except IOError as e:
        if e.errno == 2:
            raise Exception('Filename '+filename+' not found in directory '+os.getcwd() )
    
    infoList = []
    for line in fileInfo:
        tmp = line.split('=')
        infoList.append(float(tmp[1]))

    InfoStruct = Info(infoList[0],infoList[1],infoList[2],infoList[3],infoList[4],infoList[5],infoList[6])   
    return InfoStruct

# Function that gets the infeasibilities from the .lst file in the 13C problem
def getInfeasibilities(input):
    filename = input[0]
    infesFileName = 'infeasibilites.txt'
    # grep infeasibilities to file    
    call   = "grep INFES "+ filename +" | grep '\[' | grep _ -v | grep 'INFES =' -v > " + infesFileName  
    status = os.system(call)
    #if status != 0:
    #        raise Exception('Collecting infeasibilities failed')
    # Collect infesibilites
    infeasibilitiesFile = open(infesFileName)
    infeasibilities = []
    infeasibilities.append('Infeasibilities: ')
    for line in infeasibilitiesFile:
        infeasibilities.append(line)    

    return infeasibilities

# Function that gets the result of GAMS problem running 
def getSuccessful(input):
    filename = input[0]
    successFileName  = 'successfile.txt'
    # grep success to file
    call   = "grep 'Optimal solution found' " + filename + " > " + successFileName
    status = os.system(call)
    # Check if file has content
    if os.stat(successFileName)[6] == 0:
        successful = False
    else:
        successful = True
    
    return successful
    
    
    
# Function that provides Flux parameter for results from GAMSproblem
def fluxParOut(input):
    fileName = input[0]
    parName  = input[1]
    Parameter = fluxGAMSpar(parName,[])
    Parameter.read(fileName)
    return Parameter    
    
def labelingParOut(input):
    "Function that provides labeling parameter"
    fileName = input[0]
    parName  = input[1]
    Parameter = labelingGAMSpar(parName,[])
    Parameter.read(fileName)
    return Parameter
    
# Function which erases all files in a dir and dir
def eraseAllIn(dirname):
    os.chdir(dirname)
    allfiles = os.listdir('.')
    for file in allfiles:
        os.remove(file)
    dir = os.getcwd()
    os.chdir('..')
    os.removedirs(dir)

# Function which does a x vs y comparison of labeling dictionaries for given keys
def XvsYcomp(Dict1,Dict2,keys,axes,color='b',fmt='.',label='',alpha=1,markersize=10): #),titleFig=''):

    #Limiting to given keys    
    DictX = extract(Dict1,keys)
    DictY = extract(Dict2,keys)
    
    #Obtaining plot data
    x=[]  # Computational data (EMUlabel)
    y=[]  # Experimental data (fragDict)  

    for emu in DictX:
        frag = DictX[emu]
        MDV  = frag.MDV
        #for m in range(len(MDV)):
        for m in range(frag.nmeas):
            x.append(MDV[m])
            y.append(DictY[emu][m])

    #Plotting
    x = numpy.array(x)
    y = numpy.array(y)
    axes.plot(x,y,color+fmt,label=label,alpha=alpha,markersize=markersize)    
    
#    title(titleFig)

        
# Function which does a histogram comparison of labeling dictionaries for given keys         
def histcomp(Dict1,Dict2,fragments,outputFileName,titleFig,OF,save):

 # Plotting each fragment (and output to file)
    outputFile = open(outputFileName,'w')
    width = 0.35
    fig = figure(figsize=(20,10))
    fig.suptitle(titleFig+" (OF= "+str(OF)+"), Exp(red)/Comp(blue)",fontsize=20,fontweight='bold')            

    ymax  = int(len(fragments))/5+1
    index = 1        
    for fragment in sorted(fragments):
        if fragment in Dict1 and fragment in Dict2:
            if Dict2[fragment].inFit:   # Background difference depending on whether the fragment is in the fit
                BGcolor = [1,1,1]
            else:
                BGcolor = [0.92,1,0.92]
                
            ax = subplot(ymax,5,index,axisbg=BGcolor)
            title(fragment,fontsize=16)
            MDV = Dict2[fragment].MDV
            h1 = MDV
            h2 = Dict1[fragment][0:len(h1)]

            bar(numpy.arange(len(h1))-0.2,h1,width,color='r')
            bar(numpy.arange(len(h2))+0.2,h2,width,color='b')
            # Change label ticks
            ind = range(len(MDV))
            ax.set_xticks(ind)
            ax.set_xticklabels(ind)
            # Labels            
            xlabel('m',fontsize=18)
            ylabel('MDV(m)',fontsize=18)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(16)
            index = index+1
            
            # output to file
            outputFile.write("fragment:\n")
            outputFile.write(fragment+"\n")
            for m in range(min(len(h1),len(h2))):
                outputFile.write(str(m)+": "+str(h1[m])+","+str(h2[m])+"\n") 
    
    fig.tight_layout()
    subplots_adjust(top=0.9)
    
    # Save fig        
    if save != 'default':
        savefig(save) 


# Extracts keys from dictionary        
def extract(d, keys):
    return dict((k, d[k]) for k in keys if k in d)    
   
def substituteInFile(fileIn,changes):
    """
    Makes substitutions in file given by the list of list changes (e.g.):

    changes = [['maxflow13CU = (\d+)','maxflow13CU = '+str(125)],['BiomassEcoli','biomassSC4']]

    """
    # Do some input check for sanity's sake
    if changes:
        assert changes.__class__.__name__=='list'   ,  "Changes input must be a list of lists"
        assert changes[0].__class__.__name__=='list',  "Changes input must be a list of lists"
    else:
        assert changes.__class__.__name__=='list'   ,  "Changes input must be a list of lists"        


    # Get file lines
    fileName,string = file2tuple(fileIn)
    lines = string.split('\n')
               
    newlines = lines
    # Do substitutions
    for change in changes:
        lines = newlines
        # Regular expression     
        p = re.compile(change[0])
        value = str(change[1])   # Convert into string

        # Substitution
        newlines=[]
        for line in lines:        
            newlines.append(p.sub(value, line))
    
    newString = '\n'.join(newlines)

    return (fileName,newString)   
   
## Change parameters in file
#def changeParam(oldFile,parameters):
#    # Get file in tuple form
#    filename,string = GAMSclasses.file2tuple(oldFile) 
#    # Make temporary directory
#    os.mkdir('temporaryChParam')
#    os.chdir('temporaryChParam')    
#    # Make temporary file
#    outfile  = open(filename,'w') 
#    outfile.write(string)
#    outfile.close()
#    # Change parameter through sed
#    for parameter in parameters:
#        name,value = parameter
#        call = "sed -r 's/"+name+" = [0-9]+/"+name+" = "+str(value)+"/' < "+filename+" > newFile.txt"
#        os.system(call)
#    newfile = GAMSclasses.file2tuple('newFile.txt') 
#    newfile = (filename,newfile[1])
#    # Erase all files and dir
#    for file in os.listdir('.'):
#        os.remove(file)
#    #dir = os.getcwd()
#    os.chdir('..')
#    os.removedirs('temporaryChParam')
#    
#    # debug
#    #fileout = open(newfile[0],'w')
#    #fileout.write(newfile[1])
#    
#    return newfile
    
# Function to round up at a given precision
def roundUp(value,precision=0):
    precVal = 10**precision
    newValue = numpy.ceil(value*precVal)/precVal
    
    return newValue    
    
############### Tests ##################


if __name__ == "__main__":

    ala = core.met('ala',3)
    pyr = core.met('pyr',4)

    metsTest = core.metList([ala,pyr])
   
    print metsTest.carbonDict
    print metsTest.excluded
    print metsTest.source
   
    PDH = core.reaction('PDH',True)
    PGI = core.reaction('PGI')
  
    reacsTest = core.reactionList([PDH,PGI])
    print reacsTest.reacNames1
    print reacsTest.reacNames2
   
    fullTest = True
    if fullTest:
        #names = ['rf05','gpmA','pgi','zwf']
        names = ['rf05']
        figure()
        for strain in names:
            print "Strain: "+strain
            # Get sbml file
            qmodeldir         = os.environ['QUANTMODELPATH']
            dirKEIO           = qmodeldir+'/data/tests/keio/'+strain+'/' 
            #dirFinal          = '/users/hgmartin/pythontest/keiodata/'
            dirFinal          = '/scratch/hgmartin_gams_files/tests/batch/'

            REACTIONSfilename = 'REACTIONS'+strain+'.txt' 

            KEIOReactionNetwork = keio2sbml.KEIOReactionNetwork(dirKEIO+REACTIONSfilename)
            KEIOReactionNetwork.addFeed(dirKEIO+'FEED'+strain+'.txt')
            KEIOReactionNetwork.addGCMS(dirKEIO+'GCMS'+strain+'.txt')
            KEIOReactionNetwork.addMeasFluxes(dirKEIO+'FLUX'+strain+'.txt')
            KEIOReactionNetwork.write(dirFinal+'KEIO'+strain)
            
            # Get KEIO fluxes
            KEIOFluxes = keio2sbml.getKEIOFluxes(dirKEIO+'FLUX'+strain+'.txt')    

            # Get FIT fluxes
            os.chdir(dirFinal) 

            ecoliModel = C13Model('/users/hgmartin/pythontest/keiodata/KEIO'+strain+'.sbml')

            [FITFluxes,FITFluxesVar,EMUlabel,fragDict,OF] = ecoliModel.findFluxesStds(Nrep=3,Nrand=2,dirFinal=dirFinal)            

            #print "FITFluxes:"
            #print FITFluxes

            # Plotting
            i = names.index(strain)+1
            subplot('24'+str(2*int(i)-1))
            compare2KEIOFluxes(KEIOFluxes,FITFluxes,FITFluxesVar)
            xlabel('KEIO fluxes')
            ylabel('FIT fluxes')
            title(strain)
            subplot('24'+str(2*int(i)))
            compareGCMS(EMUlabel,fragDict)
            xlabel('Experimental GCMS')
            ylabel('Computational GCMS')
            title('OF = '+str(OF))
    
        show()



