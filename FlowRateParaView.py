#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# find source
slice1 = FindSource('Slice1')

# create a new 'Generate Surface Normals'
generateSurfaceNormals1 = GenerateSurfaceNormals(Input=slice1)

# find source
pvfoam = FindSource('pv.foam')

# Properties modified on generateSurfaceNormals1
generateSurfaceNormals1.ComputeCellNormals = 1

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [1233, 814]

# get color transfer function/color map for 'alpha1'
pLUT = GetColorTransferFunction('alpha1')

# show data in view
generateSurfaceNormals1Display = Show(generateSurfaceNormals1, renderView1)
# trace defaults for the display properties.
generateSurfaceNormals1Display.ColorArrayName = ['POINTS', 'alpha1']
generateSurfaceNormals1Display.LookupTable = pLUT
generateSurfaceNormals1Display.OSPRayScaleArray = 'alpha1'
generateSurfaceNormals1Display.OSPRayScaleFunction = 'PiecewiseFunction'
generateSurfaceNormals1Display.GlyphType = 'Arrow'
generateSurfaceNormals1Display.SetScaleArray = ['POINTS', 'alpha1']
generateSurfaceNormals1Display.ScaleTransferFunction = 'PiecewiseFunction'
generateSurfaceNormals1Display.OpacityArray = ['POINTS', 'alpha1']
generateSurfaceNormals1Display.OpacityTransferFunction = 'PiecewiseFunction'

# hide data in view
Hide(slice1, renderView1)

# show color bar/color legend
generateSurfaceNormals1Display.SetScalarBarVisibility(renderView1, True)

# get opacity transfer function/opacity map for 'alpha1'
pPWF = GetOpacityTransferFunction('alpha1')

# create a new 'Calculator'
calculator1 = Calculator(Input=generateSurfaceNormals1)
calculator1.Function = ''

# Properties modified on calculator1
calculator1.AttributeMode = 'Cell Data'
calculator1.ResultArrayName = 'Flow Rate (m3/s)'
calculator1.Function = 'alpha1*(Normals_X*U_X+Normals_Y*U_Y+Normals_Z*U_Z)'

# show data in view
calculator1Display = Show(calculator1, renderView1)
# trace defaults for the display properties.
calculator1Display.ColorArrayName = ['POINTS', 'alpha1']
calculator1Display.LookupTable = pLUT
calculator1Display.OSPRayScaleArray = 'alpha1'
calculator1Display.OSPRayScaleFunction = 'PiecewiseFunction'
calculator1Display.GlyphType = 'Arrow'
calculator1Display.SetScaleArray = ['POINTS', 'alpha1']
calculator1Display.ScaleTransferFunction = 'PiecewiseFunction'
calculator1Display.OpacityArray = ['POINTS', 'alpha1']
calculator1Display.OpacityTransferFunction = 'PiecewiseFunction'

# hide data in view
Hide(generateSurfaceNormals1, renderView1)

# show color bar/color legend
calculator1Display.SetScalarBarVisibility(renderView1, True)

# create a new 'Integrate Variables'
integrateVariables1 = IntegrateVariables(Input=calculator1)

# Create a new 'SpreadSheet View'
spreadSheetView1 = CreateView('SpreadSheetView')
spreadSheetView1.ColumnToSort = ''
spreadSheetView1.BlockSize = 1024L
# uncomment following to set a specific view size
# spreadSheetView1.ViewSize = [400, 400]

# get layout
layout1 = GetLayout()

# place view in the layout
layout1.AssignView(2, spreadSheetView1)

# show data in view
integrateVariables1Display = Show(integrateVariables1, spreadSheetView1)
# trace defaults for the display properties.
integrateVariables1Display.CompositeDataSetIndex = [0]

#### saving camera placements for all active views

# current camera placement for renderView1
renderView1.CameraPosition = [-34.02739655915679, 92.73693608714932, 139.1647034460014]
renderView1.CameraFocalPoint = [-13.58157110214232, 86.61777877807621, 138.20328521728513]
renderView1.CameraViewUp = [0.043618428216920434, -0.01121525633483339, 0.9989853105753004]
renderView1.CameraParallelScale = 5.52928707617364

#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).
