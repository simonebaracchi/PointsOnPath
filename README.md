# PointsOnPath

Autodesk Fusion 360 plugin for automatically placing points on vertexes with a set distance. 

It can generate points at a desired distance. The distance between the points can be customized. The tool will warn you if the path length is not a good multiple of the points distance.

The intended purpose of this tool is to mark stitching points on sewing or leather patterns.

## Installation

Download all files in this repo, place them in the `%appdata%\Autodesk\Autodesk Fusion 360\API\Scripts` (for example it might be `C:\Users\Simone\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts\PointsOnPath`), and restart Fusion 360.

In the top Fusion 360 toolbar select "Utilities", then under "Add-ins" choose "Scripts and add-ins", "Add-ins", "My add-ins", click the "+" button, find the script, add it, check "run on startup" and then click "run".

## Usage

Select a vertex, open the `Create` menu and choose `Points on path`. Then you can specify a distance between points. If the vertex length is not a multiple of the desired distance, an error will be shown.

This project is to be considered experimental.
