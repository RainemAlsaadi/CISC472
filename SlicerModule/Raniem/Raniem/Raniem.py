import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy
import math
import slicer

#
# Raniem
#

class Raniem(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Raniem" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# RaniemWidget
#

class RaniemWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # threshold value
    #
    self.imageThresholdSliderWidget = ctk.ctkSliderWidget()
    self.imageThresholdSliderWidget.singleStep = 0.1
    self.imageThresholdSliderWidget.minimum = -100
    self.imageThresholdSliderWidget.maximum = 100
    self.imageThresholdSliderWidget.value = 0.5
    self.imageThresholdSliderWidget.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    parametersFormLayout.addRow("Image threshold", self.imageThresholdSliderWidget)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = RaniemLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)

#
# RaniemLogic
#

class RaniemLogic(ScriptedLoadableModuleLogic):
  # Added this function
  def averageTransformedDistance(self,refPoints,rasPoints,referenceToRasMatrix):
      average = 0.0
      num = 0
      
      #Get the number of points
      numberOfPoints= refPoints.GetNumberOfPoints()
      bNum = rasPoints.GetNumberOfPoints()
      
      if numberOfPoints != bNum:
        logging.error('Number of points in two lists do not match')
        return -1
      
      for i in range(numberOfPoints):
        num = num + 1
        a = refPoints.GetPoint(i)
        pointA_Reference = numpy.array(a)
        pointA_Reference = numpy.append(pointA_Reference, 1)
        pointA_Ras = referenceToRasMatrix.MultiplyFloatPoint(pointA_Reference)
        b = rasPoints.GetPoint(i)
        pointB_Ras = numpy.array(b)
        pointB_Ras = numpy.append(pointB_Ras, 1)
        distance = numpy.linalg.norm(pointA_Ras - pointB_Ras)
        average = average + (distance - average) / num

      return average
    
  #Added this function  
  def rigidRegistration(self,refPoints,rasPoints,referenceToRasMatrix):
    landmarkTransform = vtk.vtkLandmarkTransform()
    landmarkTransform.SetSourceLandmarks(refPoints)
    landmarkTransform.SetTargetLandmarks(rasPoints)
    landmarkTransform.SetModeToRigidBody()
    landmarkTransform.Update()
    landmarkTransform.GetMatrix(referenceToRasMatrix)


class RaniemTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_Raniem1()
    
  #Added this function to generate points  
  def generatePoints(self, numPoints, Scale, Sigma):
    rasFids = slicer.util.getNode('RasPoints')
    if rasFids == None:
      rasFids = slicer.vtkMRMLMarkupsFiducialNode()
      rasFids.SetName('RasPoints')
      slicer.mrmlScene.AddNode(rasFids)
    rasFids.RemoveAllMarkups()

    refFids = slicer.util.getNode('ReferencePoints')
    if refFids == None:
      refFids = slicer.vtkMRMLMarkupsFiducialNode()
      refFids.SetName('ReferencePoints')
      slicer.mrmlScene.AddNode(refFids)
    refFids.RemoveAllMarkups()
    refFids.GetDisplayNode().SetSelectedColor(1, 1, 0)

    fromNormCoordinates = numpy.random.rand(numPoints, 3)
    noise = numpy.random.normal(0.0, Sigma, numPoints * 3)

    for i in range(numPoints):
      x = (fromNormCoordinates[i, 0] - 0.5) * Scale
      y = (fromNormCoordinates[i, 1] - 0.5) * Scale
      z = (fromNormCoordinates[i, 2] - 0.5) * Scale
      rasFids.AddFiducial(x, y, z)#For visualization
      xx = x + noise[i * 3]
      yy = y + noise[i * 3 + 1]
      zz = z + noise[i * 3 + 2]
      refFids.AddFiducial(xx, yy, zz)#For visualization
      
  #Added this function    
  def fiducialsToPoints(self,fiducials,points):
    n = fiducials.GetNumberOfFiducials()
    for i in range (n): 
      p = [0,0,0]
      fiducials.GetNthFiducialPosition(i,p)
      points.InsertNextPoint(p[0],p[1],p[2])


  def test_Raniem1(self):
    referenceToRas = slicer.vtkMRMLLinearTransformNode()
    referenceToRas.SetName('ReferenceToRas')
    slicer.mrmlScene.AddNode(referenceToRas)

    createModelsLogic = slicer.modules.createmodels.logic()
    rasModelNode = createModelsLogic.CreateCoordinate(20,2)
    rasModelNode.SetName('RasCoordinateModel')
    refModelNode = createModelsLogic.CreateCoordinate(20,2)
    refModelNode.SetName('ReferenceCoordinateModel')
    refModelNode.SetAndObserveTransformNodeID(referenceToRas.GetID())

    rasModelNode.GetDisplayNode().SetColor(1,0,0)
    refModelNode.GetDisplayNode().SetColor(0,1,0)

    # vtkPoints type is needed for registration

    rasPoints = vtk.vtkPoints()
    refPoints = vtk.vtkPoints()
    
    logic = RaniemLogic()
    
    numSamples=10
    
    # Create an Array Node and add some data for the chart view 
    dn2 = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    treArray = dn2.GetArray()
    #Reserve location in memory 
    treArray.SetNumberOfTuples(numSamples)
    
    for i in range(numSamples):
      numPoints = 10 + i * 5
      sigma = 3.0
      scale = 100.0
      self.generatePoints(numPoints, scale, sigma)
      rasFids = slicer.util.getNode('RasPoints')
      refFids = slicer.util.getNode('ReferencePoints')
      self.fiducialsToPoints(rasFids, rasPoints)
      self.fiducialsToPoints(refFids, refPoints)
      referenceToRasMatrix = vtk.vtkMatrix4x4()
      logic.rigidRegistration(refPoints, rasPoints, referenceToRasMatrix)
      det = referenceToRasMatrix.Determinant()
      if det < 1e-8:
        logging.error('All points in one line')
        continue
      referenceToRas.SetMatrixTransformToParent(referenceToRasMatrix)
      avgDistance = logic.averageTransformedDistance(refPoints, rasPoints, referenceToRasMatrix)
      print "Average distance: " + str(avgDistance)
      targetPoint_Ras = numpy.array([0,0,0,1])
      targetPoint_Reference = referenceToRasMatrix.MultiplyFloatPoint(targetPoint_Ras)
      targetPoint_Reference = numpy.array(targetPoint_Reference)
      tre = numpy.linalg.norm(targetPoint_Ras - targetPoint_Reference)
      
      #Added these 3 lines for the chart view 
      treArray.SetComponent(i, 0, numPoints)
      treArray.SetComponent(i, 1, tre)
      treArray.SetComponent(i, 2, 0)
      print "TRE: " + str(tre)
      print ""
      
    #Using a chart view, plot TRE as a function of number of points
    
    #Switch to a layout (24) that contains a Chart View to initiate the construction of the widget and Chart View Node
    lns = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
    lns.InitTraversal()
    ln = lns.GetNextItemAsObject()
    ln.SetViewArrangement(24)

    #Get chart view node
    cvns = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
    cvns.InitTraversal()
    cvn = cvns.GetNextItemAsObject()
  
    #Create chart node
    cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
    
    # Add the Array Nodes to the Chart. The first argument is a string used for the legend and to refer to the Array when setting properties.
    cn.AddArray('TRE',dn2.GetID())

    # Set a few properties on the Chart. The first argument is a string identifying which Array to assign the property.
    # 'default' is used to assign a property to the Chart itself (as opposed to an Array Node).
    cn.SetProperty('default', 'title', 'TRE as a Function of Number of Points')
    cn.SetProperty('default', 'xAxisLabel', 'Points')
    cn.SetProperty('default', 'yAxisLabel', 'TRE')


    # Tell the Chart View which Chart to display
    cvn.SetChartNodeID(cn.GetID())
