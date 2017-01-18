from __main__ import vtk, qt, ctk, slicer

#
# SlicerScripts
# Raniem Alsaadi
#

class SlicerScripts:
  def __init__(self, parent):
    parent.title = "Raniem Slicer Scripts"
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Raniem Alsaadi"]
    parent.helpText = """
    This assignment solution is inspired from the HelloPython tutorial. Done by Raniem Alsaadi.
    """
    parent.acknowledgementText = """
    This file is a Slicer programming assignment solution. Done by Raniem Alsaadi.
    """ # replace with organization, grant and thanks.
    self.parent = parent

#
# qHelloPythonWidget
#

class SlicerScriptsWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    # Collapsible button
    sampleCollapsibleButton = ctk.ctkCollapsibleButton()
    sampleCollapsibleButton.text = "A collapsible button"
    self.layout.addWidget(sampleCollapsibleButton)

    # Layout within the sample collapsible button
    sampleFormLayout = qt.QFormLayout(sampleCollapsibleButton)    
    helloWorldButton = qt.QPushButton("Hello world")
    helloWorldButton.toolTip = "Print 'Hello world' in standard ouput."
    sampleFormLayout.addWidget(helloWorldButton)
    helloWorldButton.connect('clicked(bool)', self.onHelloWorldButtonClicked)
    
    # Add vertical spacer
    self.layout.addStretch(1)

    # Set local var as instance attribute
    self.helloWorldButton = helloWorldButton

  def onHelloWorldButtonClicked(self):
    print ("Hello World !")    
    qt.QMessageBox.information(slicer.util.mainWindow(),'SlicerPython','HelloWorld!')
