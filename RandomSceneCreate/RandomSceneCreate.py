#Author-tattaka
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''
# Command inputs
_standard = adsk.core.DropDownCommandInput.cast(None)
_width = adsk.core.ValueCommandInput.cast(None)
_height = adsk.core.ValueCommandInput.cast(None)
_depth = adsk.core.ValueCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_field_width = adsk.core.ValueCommandInput.cast(None)
_field_height = adsk.core.ValueCommandInput.cast(None)
_object_number = adsk.core.ValueCommandInput.cast(None)
_object_width_min = adsk.core.ValueCommandInput.cast(None)
_object_width_max = adsk.core.ValueCommandInput.cast(None)
_object_height_min = adsk.core.ValueCommandInput.cast(None)
_object_height_max = adsk.core.ValueCommandInput.cast(None)

_handlers = []
def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        cmdDef = _ui.commandDefinitions.itemById('adskCuboidPythonScript')
        if not cmdDef:
            # Create a command definition.
            cmdDef = _ui.commandDefinitions.addButtonDefinition('adskCuboidPythonScript', 'Cuboid', 'Creates a cuboid component', '')

        # Connect to the command created event.
        onCommandCreated = CuboidCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command.
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CuboidCommandDestroyHandler(adsk.core.CommandEventHandler):
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
class CuboidCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
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
            standardAttrib = des.attributes.itemByName('Cuboid', 'standard')
            if standardAttrib:
                standard = standardAttrib.value

            if standard == 'English':
                _units = 'in'
            else:
                _units = 'mm'

            width = str(1)
            widthAttrib = des.attributes.itemByName('Cuboid', 'width')
            if widthAttrib:
                width = widthAttrib.value

            height = str(1)
            heightAttrib = des.attributes.itemByName('Cuboid', 'height')
            if heightAttrib:
                height = heightAttrib.value

            depth = str(1)
            depthAttrib = des.attributes.itemByName('Cuboid', 'depth')
            if depthAttrib:
                depth = depthAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            global _standard, _width, _height, _depth, _errMessage

            _standard = inputs.addDropDownCommandInput('standard', 'Standard', adsk.core.DropDownStyles.TextListDropDownStyle)
            if standard == "English":
                _standard.listItems.add('English', True)
                _standard.listItems.add('Metric', False)
            else:
                _standard.listItems.add('English', False)
                _standard.listItems.add('Metric', True)

            _width = inputs.addValueInput('width', 'Cuboid Width', _units, adsk.core.ValueInput.createByReal(float(width)))

            _height = inputs.addValueInput('height', 'Cuboid Height', _units, adsk.core.ValueInput.createByReal(float(height)))

            _depth = inputs.addValueInput('depth', 'Cuboid Depth', _units, adsk.core.ValueInput.createByReal(float(depth)))

            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

            # Connect to the command related events.
            onExecute = CuboidCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

            onInputChanged = CuboidCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            onValidateInputs = CuboidCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)

            onDestroy = CuboidCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class CuboidCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            attribs.add('Cuboid', 'standard', _standard.selectedItem.name)
            attribs.add('Cuboid', 'width', str(_width.value))
            attribs.add('Cuboid', 'height', str(_height.value))
            attribs.add('Cuboid', 'depth', str(_depth.value))

            width = _width.value
            height = _height.value
            depth = _depth.value

            # Create the cuboid.
            cuboidComp = drawCuboid(des, width, height, depth)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the inputChanged event.
class CuboidCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
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
                _width.value = _width.value
                _width.unitType = _units
                _height.value = _height.value
                _height.unitType = _units
                _depth.value = _depth.value
                _depth.unitType = _units

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the validateInputs event.
class CuboidCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)

            _errMessage.text = ''

            des = adsk.fusion.Design.cast(_app.activeProduct)

            result = getCommandInputValue(_width, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                width = result[1]

            if width <= 0:
                _errMessage.text = 'The width value should be greater than 0. It must be more than ' + des.unitsManager.formatInternalValue(0.1, _units, True)
                eventArgs.areInputsValid = False
                return

            result = getCommandInputValue(_height, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                height = result[1]

            if height <= 0:
                _errMessage.text = 'The height value should be greater than 0. It must be more than ' + des.unitsManager.formatInternalValue(0.1, _units, True)
                eventArgs.areInputsValid = False
                return

            result = getCommandInputValue(_depth, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                depth = result[1]

            if depth <= 0:
                _errMessage.text = 'The depth value should be greater than 0. It must be more than ' + des.unitsManager.formatInternalValue(0.1, _units, True)
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
