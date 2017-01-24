# Raniem Alsaadi. Student number: 06359600
###########################################################################
# CISC472 Homework for January 19 ,2016
# Create a button with a callback function. The function does not need to do anything, but print "button clicked" in the Python console.
###########################################################################
def callback():
  print "Button Clicked"

button = qt.QPushButton(‘Click Here’)
button.connect(‘clicked(),callback)
button.show()

###########################################################################
# CISC 472 Homework for January 24,2016
# Add a section to your SlicerScripts.py that creates a transform node that translates (no rotation)
###########################################################################

# Create coordinate models using the CreateModels module

createModelsLogic = slicer.modules.createmodels.logic()
ModelNode = createModelsLogic.CreateCoordinate(20,2)
ModelNode.SetName('NodeTransfer')


# Change the color of models

ModelNode.GetDisplayNode().SetColor(1,0,0)


# Create transform nodes

ModelToRas = slicer.vtkMRMLLinearTransformNode()
ModelToRas.SetName('ModelToRas')
slicer.mrmlScene.AddNode(ModelToRas)


# Set transform of the transform node

ModelToRasTransform = vtk.vtkTransform()
ModelToRasTransform.PreMultiply() # This is default, but it makes explicit
ModelToRasTransform.Translate(0, 100, 0)
ModelToRasTransform.Update()
ModelToRas.SetAndObserveTransformToParent(ModelToRasTransform)


# Transform the models with transform nodes

ModelNode.SetAndObserveTransformNodeID(ModelToRas.GetID())
