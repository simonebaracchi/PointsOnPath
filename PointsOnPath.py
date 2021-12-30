#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_handlers = []
_vertices = adsk.core.SelectionCommandInput.cast(None)
_distance = adsk.core.ValueCommandInput.cast(None)


# Event handler for the execute event.
class MyExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        # Get the input values.
        vertices = []
        for vertexCount in range(_vertices.selectionCount):
            vertices.append(_vertices.selection(vertexCount).entity)
            
        radius = _distance.value
        
        firstFeature = None
        des = adsk.fusion.Design.cast(_app.activeProduct)
        rootComp = des.rootComponent
        for vertex in vertices:
            (first, lastFeature) = pointOnPath(rootComp, vertex, radius)
            if not firstFeature:
                firstFeature = first

        tlNode = des.timeline.timelineGroups.add(firstFeature.timelineObject.index, lastFeature.timelineObject.index)
        tlNode.name = 'Point On Path'


# Event handler for the executePreview event.
class MyExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        # Get the input values.
        vertices = []
        for vertexCount in range(_vertices.selectionCount):
            vertices.append(_vertices.selection(vertexCount).entity)
            
        radius = _distance.value
        
        firstFeature = None
        des = adsk.fusion.Design.cast(_app.activeProduct)
        rootComp = des.rootComponent
        for vertex in vertices:
            (first, lastFeature) = pointOnPath(rootComp, vertex, radius)
            if not firstFeature:
                firstFeature = first

        tlNode = des.timeline.timelineGroups.add(firstFeature.timelineObject.index, lastFeature.timelineObject.index)
        tlNode.name = 'Point On Path'
        
        # Setting this to True will result in using this result as 
        # the final result and the execute event not be fired.
        eventArgs.isValidResult = True


# Event handler for the selectionEvent event.
class MySelectionEventHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.SelectionEventArgs.cast(args)

        vert = adsk.fusion.BRepVertex.cast(eventArgs.selection.entity)
        allLinear = True
        edge = adsk.fusion.BRepEdge.cast(None)
        for edge in vert.edges:
            if edge.geometry.objectType != adsk.core.Line3D.classType():
                allLinear = False
                break
        
        if allLinear:
            eventArgs.isSelectable = True
        else:
            eventArgs.isSelectable = False
            

# Event handler for the commandCreated event.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command
        inputs = cmd.commandInputs

        # Create the command inputs.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        um = des.unitsManager
        global _vertices, _distance
        _vertices = inputs.addSelectionInput('vertices', 'Vertices', 'Select the vertices.')
        _vertices.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
        _vertices.addSelectionFilter(adsk.core.SelectionCommandInput.SketchLines)
        _vertices.addSelectionFilter(adsk.core.SelectionCommandInput.ConstructionLines)
        _vertices.setSelectionLimits(1, 0)
        _distance = inputs.addValueInput('distance', 'Distance', um.defaultLengthUnits, 
                                       adsk.core.ValueInput.createByString('3.38 mm'))
                                       
        # Connect to command related events. 
        onExecute = MyExecuteHandler()
        cmd.execute.add(onExecute)
        _handlers.append(onExecute)

        onExecutePreview = MyExecutePreviewHandler()
        cmd.executePreview.add(onExecutePreview)
        _handlers.append(onExecutePreview)        

#        onSelectionEvent = MySelectionEventHandler()
#        cmd.selectionEvent.add(onSelectionEvent)
#        _handlers.append(onSelectionEvent)

        
def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Create the command definition.        
        cmdDef = _ui.commandDefinitions.addButtonDefinition('pointOnPath',
                                                            'Point on Path',
                                                            'Create Points on Path',
                                                            'Resources/PointOnPath')
                                                            
        # Connect the handler to the event.                                                    
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
    
        # Add the button to the ADD-INS panel.
        addInsPanel = _ui.allToolbarPanels.itemById('SketchPanel')
        addInsPanel.controls.addCommand(cmdDef)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        cmdDef = _ui.commandDefinitions.itemById('pointOnPath')
        if cmdDef:
            cmdDef.deleteMe()

        addInsPanel = _ui.allToolbarPanels.itemById('SketchPanel')
        control = addInsPanel.controls.itemById('pointOnPath')
        if control:
            control.deleteMe()
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Draw a sphere in the specific component at the vertex using the radius.
def pointOnPath(comp, edge, distance):
    try:
        # Get one of the edges connected to the vertex.

        #sketch
        skt = edge.parentSketch        
        
        #WorldGeometry
        crv = edge.worldGeometry
        
        #evaluator
        eva = crv.evaluator
        
        #startPoint&endPoint
        returnValue, startPoint, endPoint = eva.getEndPoints()
        if not returnValue :
            _ui.messageBox('getEndPoints_NG')
            return

        (retVal, pathMin, pathMax) = eva.getParameterExtents()
        returnValue, total_length = eva.getLengthAtParameter(pathMin, pathMax)
        if not returnValue :
            _ui.messageBox('getlength failed')
            return
        if (total_length % distance) > (distance * 0.05) and (total_length % distance) < (distance * 0.95):
            _ui.messageBox('Length is not a multiple of distance: ' + str(total_length) + ' error is ' + str(total_length % distance) + ' max allowed ' + str(distance * 0.05))


        #start parameter
        returnValue, start_prm = eva.getParameterAtPoint(startPoint)
        if not returnValue :
            _ui.messageBox('getParameterAtPoint_NG')
            return

        progress = 0
        while progress < total_length:
            # Parameter at distance
            returnValue, length_param = eva.getParameterAtLength(start_prm, progress)
            if not returnValue :
                _ui.messageBox('getParameterAtLength_NG')
                return
            #_ui.messageBox('Length is ' + str(total_length) + ' searching point at ' + str(progress))
            
            # make point
            returnValue, pnt3d = eva.getPointAtParameter(length_param)
            if not returnValue :
                _ui.messageBox('getPointAtParameter_NG')
                return
            
            #to sketchPoints
            skt_point = skt.sketchPoints.add(pnt3d)
            
            progress += distance
   
    except:
        _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
