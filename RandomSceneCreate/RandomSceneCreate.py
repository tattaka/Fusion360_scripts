#Author-tattaka
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math
import random

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''
# Command inputs
_standard = adsk.core.DropDownCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_fieldWidth = adsk.core.ValueCommandInput.cast(None)
_fieldHeight = adsk.core.ValueCommandInput.cast(None)
_objectNumber = adsk.core.StringValueCommandInput.cast(None)
_objectWidthMin = adsk.core.ValueCommandInput.cast(None)
_objectWidthMax = adsk.core.ValueCommandInput.cast(None)
_objectHeightMin = adsk.core.ValueCommandInput.cast(None)
_objectHeightMax = adsk.core.ValueCommandInput.cast(None)
_objectDepthMin = adsk.core.ValueCommandInput.cast(None)
_objectDepthMax = adsk.core.ValueCommandInput.cast(None)
_cuboidEnable = adsk.core.BoolValueCommandInput.cast(None)
_sphereEnable = adsk.core.BoolValueCommandInput.cast(None)
_poleEnable = adsk.core.BoolValueCommandInput.cast(None)

_handlers = []
def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        cmdDef = _ui.commandDefinitions.itemById('adskRandomSceneCreatePythonScript')
        if not cmdDef:
            # Create a command definition.
            cmdDef = _ui.commandDefinitions.addButtonDefinition('adskRandomSceneCreatePythonScript', 'RandomSceneCreate', 'Creates a RandomScene', '')

        # Connect to the command created event.
        onCommandCreated = RandomSceneCreateCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command.
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class RandomSceneCreateCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Verfies that a value command input has a valid expression and returns the
# value if it does.  Otherwise it returns False.  This works around a
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager

        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandCreated event.
class RandomSceneCreateCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()

            defaultUnits = des.unitsManager.defaultLengthUnits

            # Determine whether to use inches or millimeters as the intial default.
            global _units
            if defaultUnits == 'in' or defaultUnits == 'ft':
                _units = 'in'
            else:
                _units = 'mm'

            # Define the default values and get the previous values from the attributes.
            if _units == 'in':
                standard = 'English'
            else:
                standard = 'Metric'
            standardAttrib = des.attributes.itemByName('RandomSceneCreate', 'standard')
            if standardAttrib:
                standard = standardAttrib.value

            if standard == 'English':
                _units = 'in'
            else:
                _units = 'mm'

            fieldWidth = str(20)
            fieldWidthAttrib = des.attributes.itemByName('RandomSceneCreate', 'fieldWidth')
            if fieldWidthAttrib:
                fieldWidth = fieldWidthAttrib.value

            fieldHeight = str(20)
            fieldHeightAttrib = des.attributes.itemByName('RandomSceneCreate', 'fieldHeight')
            if fieldHeightAttrib:
                fieldHeight = fieldHeightAttrib.value

            objectNumber = '1'
            objectNumberAttrib = des.attributes.itemByName('RandomSceneCreate', 'objectNumber')
            if objectNumberAttrib:
                objectNumber = objectNumberAttrib.value

            objectWidthMin = str(1)
            objectWidthMinAttrib = des.attributes.itemByName('RandomSceneCreate', 'objectWidthMin')
            if objectWidthMinAttrib:
                objectWidthMin = objectWidthMinAttrib.value

            objectWidthMax = str(5)
            objectWidthMaxAttrib = des.attributes.itemByName('RandomSceneCreate', 'objectWidthMax')
            if objectWidthMaxAttrib:
                objectWidthMax = objectWidthMaxAttrib.value

            objectHeightMin = str(1)
            objectHeightMinAttrib = des.attributes.itemByName('RandomSceneCreate', 'objectHeightMin')
            if objectHeightMinAttrib:
                objectHeightMin = objectHeightMinAttrib.value

            objectHeightMax = str(1)
            objectHeightMaxAttrib = des.attributes.itemByName('RandomSceneCreate', 'objectHeightMax')
            if objectHeightMaxAttrib:
                objectHeightMax = objectHeightMaxAttrib.value

            objectDepthMin = str(1)
            objectDepthMinAttrib = des.attributes.itemByName('RandomSceneCreate', 'objectDepthMin')
            if objectDepthMinAttrib:
                objectDepthMin = objectDepthMinAttrib.value

            objectDepthMax = str(5)
            objectDepthMaxAttrib = des.attributes.itemByName('RandomSceneCreate', 'objectDepthMax')
            if objectDepthMaxAttrib:
                objectDepthMax = objectDepthMaxAttrib.value

            cuboidEnable = False
            cuboidEnableAttrib = des.attributes.itemByName('RandomSceneCreate', 'cuboidEnable')
            if cuboidEnableAttrib:
                cuboidEnable = cuboidEnableAttrib.value

            sphereEnable = False
            sphereEnableAttrib = des.attributes.itemByName('RandomSceneCreate', 'sphereEnable')
            if sphereEnableAttrib:
                sphereEnable = sphereEnableAttrib.value

            poleEnable = False
            poleEnableAttrib = des.attributes.itemByName('RandomSceneCreate', 'poleEnable')
            if poleEnableAttrib:
                poleEnable = poleEnableAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            global _standard, _fieldWidth, _fieldHeight, _objectNumber, _objectWidthMin, _objectWidthMax, _objectHeightMin, _objectHeightMax, _objectDepthMin, _objectDepthMax, _cuboidEnable, _sphereEnable, _poleEnable, _errMessage

            _standard = inputs.addDropDownCommandInput('standard', 'Standard', adsk.core.DropDownStyles.TextListDropDownStyle)
            if standard == "English":
                _standard.listItems.add('English', True)
                _standard.listItems.add('Metric', False)
            else:
                _standard.listItems.add('English', False)
                _standard.listItems.add('Metric', True)

            _fieldWidth = inputs.addValueInput('fieldWidth', 'field Width', _units, adsk.core.ValueInput.createByReal(float(fieldWidth)))

            _fieldHeight = inputs.addValueInput('fieldHeight', 'field Height', _units, adsk.core.ValueInput.createByReal(float(fieldHeight)))

            _objectNumber = inputs.addStringValueInput('objectNumber', 'object Number', objectNumber)
            #_ui.messageBox(str(int(float(objectNumber))))

            _objectWidthMin = inputs.addValueInput('objectWidthMin', 'object Width Min', _units, adsk.core.ValueInput.createByReal(float(objectWidthMin)))

            _objectWidthMax = inputs.addValueInput('objectWidthMax', 'object Width Max', _units, adsk.core.ValueInput.createByReal(float(objectWidthMax)))

            _objectHeightMin = inputs.addValueInput('objectHeightMin', 'object Height Min', _units, adsk.core.ValueInput.createByReal(float(objectHeightMin)))

            _objectHeightMax = inputs.addValueInput('objectHeightMax', 'object Height Max', _units, adsk.core.ValueInput.createByReal(float(objectHeightMax)))

            _objectDepthMin = inputs.addValueInput('objectDepthMin', 'object Depth Min', _units, adsk.core.ValueInput.createByReal(float(objectDepthMin)))

            _objectDepthMax = inputs.addValueInput('objectDepthMax', 'object Depth Max', _units, adsk.core.ValueInput.createByReal(float(objectDepthMax)))

            _cuboidEnable = inputs.addBoolValueInput('cuboidEnable', 'cuboid Enable', True, '', True)

            _sphereEnable = inputs.addBoolValueInput('sphereEnable', 'sphere Enable', True, '', True)

            _poleEnable = inputs.addBoolValueInput('poleEnable', 'pole Enable', True, '', True)

            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

            # Connect to the command related events.
            onExecute = RandomSceneCreateCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

            onInputChanged = RandomSceneCreateCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            onValidateInputs = RandomSceneCreateCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)

            onDestroy = RandomSceneCreateCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class RandomSceneCreateCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            attribs.add('RandomSceneCreate', 'standard', _standard.selectedItem.name)
            attribs.add('RandomSceneCreate', 'fieldWidth', str(_fieldWidth.value))
            attribs.add('RandomSceneCreate', 'fieldHeight', str(_fieldHeight.value))
            attribs.add('RandomSceneCreate', 'objectNumber', str(_objectNumber.value))
            attribs.add('RandomSceneCreate', 'objectWidthMin', str(_objectWidthMin.value))
            attribs.add('RandomSceneCreate', 'objectWidthMax', str(_objectWidthMax.value))
            attribs.add('RandomSceneCreate', 'objectHeightMin', str(_objectHeightMin.value))
            attribs.add('RandomSceneCreate', 'objectHeightMax', str(_objectHeightMax.value))
            attribs.add('RandomSceneCreate', 'objectDepthMin', str(_objectDepthMin.value))
            attribs.add('RandomSceneCreate', 'objectDepthMax', str(_objectDepthMax.value))
            attribs.add('RandomSceneCreate', 'cuboidEnable', str(_cuboidEnable.value))
            attribs.add('RandomSceneCreate', 'sphereEnable', str(_sphereEnable.value))
            attribs.add('RandomSceneCreate', 'poleEnable', str(_poleEnable.value))

            fieldWidth = _fieldWidth.value
            fieldHeight = _fieldHeight.value
            objectNumber = int(_objectNumber.value)
            objectWidthMin = _objectWidthMin.value
            objectWidthMax = _objectWidthMax.value
            objectHeightMin = _objectHeightMin.value
            objectHeightMax = _objectHeightMax.value
            objectDepthMin = _objectDepthMin.value
            objectDepthMax = _objectDepthMax.value
            cuboidEnable = _cuboidEnable.value
            sphereEnable = _sphereEnable.value
            poleEnable = _poleEnable.value

            # Create the cuboid.
            #cuboidComp = drawCuboid(des, width, height, depth)
            compScene = createScene(des, fieldWidth, fieldHeight, objectNumber, objectWidthMin, objectWidthMax, objectHeightMin, objectHeightMax, objectDepthMin, objectDepthMax, cuboidEnable, sphereEnable, poleEnable)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the inputChanged event.
class RandomSceneCreateCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            global _units
            if changedInput.id == 'standard':
                if _standard.selectedItem.name == 'English':

                    _units = 'in'
                elif _standard.selectedItem.name == 'Metric':

                    _units = 'mm'

                # Set each one to it's current value because otherwised if the user
                # has edited it, the value won't update in the dialog because
                # apparently it remembers the units when the value was edited.
                # Setting the value using the API resets this.
                _fieldWidth.value = _fieldWidth.value
                _fieldWidth.unitType = _units
                _fieldHeight.value = _fieldHeight.value
                _fieldHeight.unitType = _units
                _objectNumber.value = int(_objectNumber.value)
                #_objectNumber.unitType = _units
                _objectWidthMin.value = _objectWidthMin.value
                _objectWidthMin.unitType = _units
                _objectWidthMax.value = _objectWidthMax.value
                _objectWidthMax.unitType = _units
                _objectHeightMin.value = _objectHeightMin.value
                _objectHeightMin.unitType = _units
                _objectHeightMax.value = _objectHeightMax.value
                _objectHeightMax.unitType = _units
                _objectDepthMin.value = _objectDepthMin.value
                _objectDepthMin.unitType = _units
                _objectDepthMax.value = _objectDepthMax.value
                _objectDepthMax.unitType = _units
                _cuboidEnable.value = _cuboidEnable.value
                _cuboidEnable.unitType = _units
                _sphereEnable.value = _sphereEnable.value
                _sphereEnable.unitType = _units
                _poleEnable.value = _poleEnable.value
                _poleEnable.unitType = _units

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the validateInputs event.
class RandomSceneCreateCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)

            _errMessage.text = ''

            des = adsk.fusion.Design.cast(_app.activeProduct)

            if not _objectNumber.value.isdigit():
                _errMessage.text = 'The number of object must be a whole number.'
                eventArgs.areInputsValid = False
                return
            else:
                objectNumber = int(_objectNumber.value)

            if objectNumber <= 0:
                _errMessage.text = 'The number of teeth must be 1 or more.'
                eventArgs.areInputsValid = False
                return

            result = getCommandInputValue(_fieldWidth, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                fieldWidth = result[1]

            if fieldWidth <= 0:
                _errMessage.text = 'The width value should be greater than 0. It must be more than ' + des.unitsManager.formatInternalValue(0, _units, True)
                eventArgs.areInputsValid = False
                return

            result = getCommandInputValue(_fieldHeight, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                fieldHeight = result[1]

            if fieldHeight <= 0:
                _errMessage.text = 'The height value should be greater than 0. It must be more than ' + des.unitsManager.formatInternalValue(0, _units, True)
                eventArgs.areInputsValid = False
                return

            result = getCommandInputValue(_objectWidthMin, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                objectWidthMin = result[1]

            if objectWidthMin <= 0:
                _errMessage.text = 'The objectWidthMin should be greater than 0. It must be more than ' + des.unitsManager.formatInternalValue(0, _units, True)
                eventArgs.areInputsValid = False
                return

            result = getCommandInputValue(_objectWidthMax, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                objectWidthMax = result[1]

            if objectWidthMax <= 0 or objectWidthMax < objectWidthMin:
                _errMessage.text = 'The objectWidthMax should be greater than 0. Or objectWidthMax < objectWidthMin. It must be more than ' + des.unitsManager.formatInternalValue(objectWidthMin + 1, _units, True)
                eventArgs.areInputsValid = False
                return

            result = getCommandInputValue(_objectHeightMin, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                objectHeightMin = result[1]

            if objectHeightMin <= 0:
                _errMessage.text = 'The objectHeightMin should be greater than 0. It must be more than ' + des.unitsManager.formatInternalValue(0, _units, True)
                eventArgs.areInputsValid = False
                return

            result = getCommandInputValue(_objectHeightMax, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                objectHeightMax = result[1]

            if objectHeightMax <= 0 or objectHeightMax < objectHeightMin:
                _errMessage.text = 'The objectHeightMax should be greater than 0. Or objectHeightMax < objectHeightMin. It must be more than ' + des.unitsManager.formatInternalValue(objectHeightMin + 1, _units, True)
                eventArgs.areInputsValid = False
                return

            result = getCommandInputValue(_objectDepthMin, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                objectDepthMin = result[1]

            if objectDepthMin <= 0:
                _errMessage.text = 'The objectDepthMin should be greater than 0. It must be more than ' + des.unitsManager.formatInternalValue(0, _units, True)
                eventArgs.areInputsValid = False
                return

            result = getCommandInputValue(_objectDepthMax, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                objectDepthMax = result[1]

            if objectDepthMax <= 0 or objectDepthMax < objectDepthMin:
                _errMessage.text = 'The objectDepthMax should be greater than 0. Or objectDepthMax < objectDepthMin. It must be more than ' + des.unitsManager.formatInternalValue(objectDepthMin + 1, _units, True)
                eventArgs.areInputsValid = False
                return

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Builds a spur cuboid.
def drawCuboid(design, width, height, depth):
    try:
        # Create a new component by creating an occurrence.
        occs = design.rootComponent.occurrences
        mat = adsk.core.Matrix3D.create()
        newOcc = occs.addNewComponent(mat)
        newComp = adsk.fusion.Component.cast(newOcc.component)

        # Create a new sketch.
        sketches = newComp.sketches
        xyPlane = newComp.xYConstructionPlane
        baseSketch = sketches.add(xyPlane)

        # Draw a rectangle for the base.
        baseSketch.sketchCurves.sketchLines.addCenterPointRectangle(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(width/2,height/2,0))

        #### Extrude the circle to create the base of the cuboid.
        prof = adsk.fusion.Profile.cast(None)
        prof = baseSketch.profiles.item(0)

        # Create an extrusion input to be able to define the input needed for an extrusion
        # while specifying the profile and that a new component is to be created
        extrudes = newComp.features.extrudeFeatures
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Define that the extent is a distance extent of 5 cm.
        distance = adsk.core.ValueInput.createByReal(depth)
        extInput.setDistanceExtent(False, distance)

        # Create the extrusion.
        baseExtrude = extrudes.add(extInput)
        # Create an extrusion input to be able to define the input needed for an extrusion
        # while specifying the profile and that a new component is to be created
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.JoinFeatureOperation)

        # Define that the extent is a distance extent of 5 cm.
        distance = adsk.core.ValueInput.createByReal(depth)
        extInput.setDistanceExtent(False, distance)

        baseFillet = None

        # Group everything used to create the cuboid in the timeline.
        timelineGroups = design.timeline.timelineGroups
        newOccIndex = newOcc.timelineObject.index
        diametralPitchSketch = sketches.add(xyPlane)
        pitchSketchIndex = diametralPitchSketch.timelineObject.index
        # ui.messageBox("Indices: " + str(newOccIndex) + ", " + str(pitchSketchIndex))
        timelineGroup = timelineGroups.add(newOccIndex, pitchSketchIndex)
        timelineGroup.name = 'Cuboid'

        # Add an attribute to the component with all of the input values.  This might
        # be used in the future to be able to edit the cuboid.
        cuboidValues = {}
        cuboidValues['width'] = str(width)
        cuboidValues['height'] = str(height)
        cuboidValues['depth'] = str(depth)
        attrib = newComp.attributes.add('Cuboid', 'Values',str(cuboidValues))

        newComp.name = 'Cuboid (' + str(width*10) + "mm" + ' x ' + str(height*10) + "mm" + ' x ' + str(depth*10) + "mm" + ')'
        return newComp
    except Exception as error:
        _ui.messageBox("drawCuboid Failed : " + str(error))
        return None

def createScene(design, fieldWidth, fieldHeight, objectNumber, objectWidthMin, objectWidthMax, objectHeightMin, objectHeightMax, objectDepthMin, objectDepthMax, cuboidEnable, sphereEnable, poleEnable):
    try:
        pass
    except Exception as error:
        _ui.messageBox("drawCuboid Failed : " + str(error))
        return None
