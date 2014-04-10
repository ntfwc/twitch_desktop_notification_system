##    Copyright (C) 2014 ntfwc
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PIL import Image
from StringIO import StringIO

def parseDataToImage(data):
    return Image.open(StringIO(data))

import gtk
import numpy

def convertImageToGTKPixBuf(image):
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    arr = numpy.array(image)
    return gtk.gdk.pixbuf_new_from_array(arr, gtk.gdk.COLORSPACE_RGB, 8)

def restrictWidthAndHeightByRescaling(image, maxWidthOrHeight):
    width, height = image.size
    if width > height:
        if width > maxWidthOrHeight:
            newWidth = maxWidthOrHeight
            newHeight = height * newWidth/width
            newSize = (newWidth, newHeight)
            return image.resize(newSize, Image.ANTIALIAS)
    else:
        if height > maxWidthOrHeight:
            newHeight = maxWidthOrHeight
            newWidth = width * newHeight/height
            newSize = (newWidth, newHeight)
            return image.resize(newSize, Image.ANTIALIAS)
    return image
            

def parseDataToPixBuf(data):
    image = parseDataToImage(data)
    return convertImageToGTKPixBuf(image)

##def parseImageFileToPixBuf(filePath):
##    image = Image.open(filePath)
##    return convertImageToGTKPixBuf(image)
##
##def parseDataToPixBufAndRestrictSize(data, maxWidthOrHeight):
##    image = parseDataToImage(data)
##    image = restrictWidthAndHeightByRescaling(image, maxWidthOrHeight)
##    return convertImageToGTKPixBuf(image)
##
##def parseImageFileToPixBufAndRestrictSize(filePath, maxWidthOrHeight):
##    image = Image.open(filePath)
##    image = restrictWidthAndHeightByRescaling(image, maxWidthOrHeight)
##    return convertImageToGTKPixBuf(image)

def exportImageAsPNGByteString(image):
    byteStringBuffer = StringIO()
    image.save(byteStringBuffer, "PNG")
    return byteStringBuffer.getvalue()

def filterImageDataToVersionWithinSizeRestriction(imageData, maxWidthOrHeight):
    image = parseDataToImage(imageData)
    width, height = image.size
    if width > maxWidthOrHeight or height > maxWidthOrHeight:
        image = restrictWidthAndHeightByRescaling(image, maxWidthOrHeight)
        return exportImageAsPNGByteString(image)
    else:
        return imageData

