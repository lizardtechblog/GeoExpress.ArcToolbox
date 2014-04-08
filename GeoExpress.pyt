import arcpy
import subprocess
import tempfile
import os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox."""
        self.label = "GeoExpress Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [AOI, Compress, Crop, Despeckle, EditMetadata, Reproject]
    
def getGXVersion():
    """Determine the version of GeoExpress that needs to be called."""
    gxVersionList = ['mrsidgeoencoder', 'mrsidgeoencoderU', 'mrsidgeoencoderT', 'mrsidgeoencoderTS']
    gxVersion = ''
            
    for cmd in gxVersionList:
            try:
                subprocess.call(cmd + ' -v', shell=False)
                gxVersion = cmd
                return gxVersion
            except OSError:
                continue
    
    if gxVersion == '':
        arcpy.AddError("Could not find GeoExpress. Make sure that GeoExpress is in your Path.")
        exit(1)


class AOI(object):
    def __init__(self):
        """Area of Interest Tool"""
        self.label = "Area of Interest Tool"
        self.description = "Enter the width, height, upper left X, and upper left Y coordinates of the area of interest."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions."""
        in_file = arcpy.Parameter(
			displayName = "Input File",
			name = "in_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Input")
        
        out_file = arcpy.Parameter(
			displayName = "Output File",
			name = "out_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Output")
        
        aoi_ulx = arcpy.Parameter(
			displayName = "Upper Left X",
			name = "aoi_ulx",
			datatype = "Long",
			parameterType = "Required",
			direction = "Input")
            
        aoi_uly = arcpy.Parameter(
			displayName = "Upper Left Y",
			name = "aoi_uly",
			datatype = "Long",
			parameterType = "Required",
			direction = "Input")
            
        aoi_width = arcpy.Parameter(
			displayName = "Width",
			name = "aoi_width",
			datatype = "Long",
			parameterType = "Required",
			direction = "Input")
            
        aoi_height = arcpy.Parameter(
			displayName = "Height",
			name = "aoi_height",
			datatype = "Long",
			parameterType = "Required",
			direction = "Input")
            
        aoi_mask = arcpy.Parameter(
            displayName = "Mask Type",
            name = "aoi_mask",
            datatype = "String",
            parameterType = "Required",
            direction = "Input")
        
        aoi_mask.filter.type = "ValueList"
        aoi_mask.filter.list = ["Inner", "Outer"]
        
        compression_ratio = arcpy.Parameter(
			displayName = "Compression Ratio",
			name = "compression_ratio",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")

        params = [in_file, out_file, aoi_ulx, aoi_uly, aoi_width, aoi_height, aoi_mask, compression_ratio]
        return params

    def updateMessages(self, parameters):
        """Compression Ratio must be a whole number greater than 0."""
        err_not_number = "The compression ratio must be a whole number."
        err_negative_value = "The compression ratio cannot be a negative number."
        compression_ratio = parameters[-1].valueAsText
        
        if compression_ratio:
            try:
                int(compression_ratio)
                if int(compression_ratio) < 0:
                    parameters[-1].setErrorMessage(err_negative_value)
            except ValueError:
                parameters[-1].setErrorMessage(err_not_number)
                
        return   
    
    def execute(self, parameters, messages):
        """Parse the parameters for GeoExpress."""
        aoi_string = getGXVersion() + ' -i "' + parameters[0].valueAsText + '" -o "' + parameters[1].valueAsText + \
            '" -aoiulxy ' + parameters[2].valueAsText + ' ' + parameters[3].valueAsText + ' -aoiwh ' + \
            parameters[4].valueAsText + ' ' + parameters[5].valueAsText
            
        """Add the mask type."""
        if parameters[6].valueAsText == "Inner":
            aoi_string = aoi_string + ' -aoimaskinner'
        else:
            aoi_string = aoi_string + ' -aoimaskouter'
            
        """If you specify a compression ratio, append it to the command."""
        if parameters[-1].valueAsText:
            aoi_string = aoi_string + ' -cr ' + parameters[-1].valueAsText
        
        subprocess.call(aoi_string, shell=False)
        return
        
class Compress(object):
    def __init__(self):
        """Compression Tool"""
        self.label = "Compression Tool"
        self.description = "Enter a compression ratio. For example, enter 20 for a compression ratio of 20:1.\
            Alternatively, leave the compression ratio field blank for lossless compression."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions."""
        in_file = arcpy.Parameter(
			displayName = "Input File",
			name = "in_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Input")
        
        out_file = arcpy.Parameter(
			displayName = "Output File",
			name = "out_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Output")
        
        compression_ratio = arcpy.Parameter(
			displayName = "Compression Ratio",
			name = "compression_ratio",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
                   
        params = [in_file, out_file, compression_ratio]
        return params

    def updateMessages(self, parameters):
        """Compression Ratio must be a whole number greater than 0."""
        err_not_number = "The compression ratio must be a whole number."
        err_negative_value = "The compression ratio cannot be a negative number."
        compression_ratio = parameters[-1].valueAsText
        
        if compression_ratio:
            try:
                int(compression_ratio)
                if int(compression_ratio) < 0:
                    parameters[-1].setErrorMessage(err_negative_value)
            except ValueError:
                parameters[-1].setErrorMessage(err_not_number)
                
        return   
    
    def execute(self, parameters, messages):
        """Parse the parameters for GeoExpress."""
        compress_string = getGXVersion() + ' -i "' + parameters[0].valueAsText + '" -o "' + parameters[1].valueAsText
        
        """If you specify a compression ratio, append it to the command."""
        if parameters[-1].valueAsText:
            compress_string = compress_string + '" -cr ' + parameters[-1].valueAsText
        
        subprocess.call(compress_string, shell=False)
        return
        
class Crop(object):
    def __init__(self):
        """Crop Tool"""
        self.label = "Crop Tool"
        self.description = "Enter the width and height of the output image and enter the upper left X and Y coordinates."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions."""
        in_file = arcpy.Parameter(
			displayName = "Input File",
			name = "in_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Input")
        
        out_file = arcpy.Parameter(
			displayName = "Output File",
			name = "out_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Output")
        
        crop_ulx = arcpy.Parameter(
			displayName = "Upper Left X",
			name = "crop_ulx",
			datatype = "Long",
			parameterType = "Required",
			direction = "Input")
            
        crop_uly = arcpy.Parameter(
			displayName = "Upper Left Y",
			name = "crop_uly",
			datatype = "Long",
			parameterType = "Required",
			direction = "Input")
            
        crop_width = arcpy.Parameter(
			displayName = "Width",
			name = "crop_width",
			datatype = "Long",
			parameterType = "Required",
			direction = "Input")
            
        crop_height = arcpy.Parameter(
			displayName = "Height",
			name = "crop_height",
			datatype = "Long",
			parameterType = "Required",
			direction = "Input")
        
        compression_ratio = arcpy.Parameter(
			displayName = "Compression Ratio",
			name = "compression_ratio",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        params = [in_file, out_file, crop_ulx, crop_uly, crop_width, crop_height, compression_ratio]
        return params

    def updateMessages(self, parameters):
        """Compression Ratio must be a whole number greater than 0."""
        err_not_number = "The compression ratio must be a whole number."
        err_negative_value = "The compression ratio cannot be a negative number."
        compression_ratio = parameters[-1].valueAsText
        
        if compression_ratio:
            try:
                int(compression_ratio)
                if int(compression_ratio) < 0:
                    parameters[-1].setErrorMessage(err_negative_value)
            except ValueError:
                parameters[-1].setErrorMessage(err_not_number)
                
        return   
    
    def execute(self, parameters, messages):
        """Parse the parameters for GeoExpress."""
        crop_string = getGXVersion() + ' -i "' + parameters[0].valueAsText + '" -o "' + parameters[1].valueAsText + \
            '" -cropulxy ' + parameters[2].valueAsText + ' ' + parameters[3].valueAsText + ' -cropwh ' + \
            parameters[4].valueAsText + ' ' + parameters[5].valueAsText
        
        """If you specify a compression ratio, append it to the command."""
        if parameters[-1].valueAsText:
            crop_string = crop_string + ' -cr ' + parameters[-1].valueAsText
        
        subprocess.call(crop_string, shell=False)
        return

class Despeckle(object):
    def __init__(self):
        """Despeckle Tool"""
        self.label = "Despeckle Tool"
        self.description = "Enter a value for the despeckling threshold and spacing."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions."""
        in_file = arcpy.Parameter(
			displayName = "Input File",
			name = "in_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Input")
        
        out_file = arcpy.Parameter(
			displayName = "Output File",
			name = "out_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Output")
            
        ds_threshold = arcpy.Parameter(
			displayName = "Despeckling Threshold",
			name = "ds_threshold",
			datatype = "Long",
			parameterType = "Required",
			direction = "Input")
            
        ds_spacing = arcpy.Parameter(
			displayName = "Despeckling Spacing",
			name = "ds_spacing",
			datatype = "Long",
			parameterType = "Required",
			direction = "Input")
        
        compression_ratio = arcpy.Parameter(
			displayName = "Compression Ratio",
			name = "compression_ratio",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        """Set default values for despeckling."""
        ds_threshold.value = '8'
        ds_spacing.value = '6'
        
        params = [in_file, out_file, ds_threshold, ds_spacing, compression_ratio]
        return params

    def updateMessages(self, parameters):
        """Compression Ratio must be a whole number greater than 0."""
        err_not_number = "The compression ratio must be a whole number."
        err_negative_value = "The compression ratio cannot be a negative number."
        compression_ratio = parameters[-1].valueAsText
        
        if compression_ratio:
            try:
                int(compression_ratio)
                if int(compression_ratio) < 0:
                    parameters[-1].setErrorMessage(err_negative_value)
            except ValueError:
                parameters[-1].setErrorMessage(err_not_number)
                
        """Despeckling Threshold and Spacing must be greater than 1."""
        err_threshold = "The value for the despeckling threshold must be equal to or greater than 1."
        err_spacing = "The value for the despeckling spacing must be equal to or greater than 1."
        ds_threshold = parameters[2].value
        ds_spacing = parameters[3].value
        
        if ds_threshold < 1:
            parameters[2].setErrorMessage(err_threshold)
        
        if ds_spacing < 1:
            parameters[3].setErrorMessage(err_spacing)
                
        return 
    
    def execute(self, parameters, messages):
        """Parse the parameters for GeoExpress."""
        despeckle_string = getGXVersion() + ' -i "' + parameters[0].valueAsText + '" -o "' + parameters[1].valueAsText + \
            '" -ds true -dsthreshold ' + parameters[2].valueAsText + ' -dsspacing ' + parameters[3].valueAsText
        
        """If you specify a compression ratio, append it to the command."""
        if parameters[-1].valueAsText:
            despeckle_string = despeckle_string + ' -cr ' + parameters[-1].valueAsText
            
        subprocess.call(despeckle_string, shell=False)
        return

class EditMetadata(object):
    def __init__(self):
        """Edit Metadata Tool"""
        self.label = "Edit Metadata Tool"
        self.description = "Enter custom metadata in the fields below."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions."""
        in_file = arcpy.Parameter(
			displayName = "Input File",
			name = "in_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Input")
        
        out_file = arcpy.Parameter(
			displayName = "Output File",
			name = "out_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Output")
            
        company_name = arcpy.Parameter(
			displayName = "Company Name",
			name = "company_name",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")

        copyright = arcpy.Parameter(
			displayName = "Copyright",
			name = "copyright",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        credit = arcpy.Parameter(
			displayName = "Credit",
			name = "credit",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        summary = arcpy.Parameter(
			displayName = "Summary",
			name = "summary",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        keywords = arcpy.Parameter(
			displayName = "Keywords",
			name = "keywords",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        comments = arcpy.Parameter(
			displayName = "Comments",
			name = "comments",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        image_ID = arcpy.Parameter(
			displayName = "Image ID",
			name = "image_ID",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        imaging_date = arcpy.Parameter(
			displayName = "Imaging Date",
			name = "imaging_date",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        imaging_time = arcpy.Parameter(
			displayName = "Imaging Time",
			name = "imaging_time",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        source_device = arcpy.Parameter(
			displayName = "Source Device",
			name = "source_device",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        scan_info = arcpy.Parameter(
			displayName = "Scan Info",
			name = "scan_info",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        geo_location = arcpy.Parameter(
			displayName = "Geographic Location",
			name = "geo_location",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
        
        compression_ratio = arcpy.Parameter(
			displayName = "Compression Ratio",
			name = "compression_ratio",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
            
        params = [in_file, out_file, company_name, copyright, credit, summary, keywords, \
            comments, image_ID, imaging_date, imaging_time, source_device, scan_info, \
            geo_location, compression_ratio]
        return params

    def updateMessages(self, parameters):
        """Compression Ratio must be a whole number greater than 0."""
        err_not_number = "The compression ratio must be a whole number."
        err_negative_value = "The compression ratio cannot be a negative number."
        compression_ratio = parameters[-1].valueAsText
        
        if compression_ratio:
            try:
                int(compression_ratio)
                if int(compression_ratio) < 0:
                    parameters[-1].setErrorMessage(err_negative_value)
            except ValueError:
                parameters[-1].setErrorMessage(err_not_number)
                
        return 
    
    def execute(self, parameters, messages):
        """If the user enters metadata tags, iterate through the tags 
        and create a temporary text file to pass to GeoExpress."""
        temp = tempfile.NamedTemporaryFile(delete=False)
        
        for x in xrange (2, 14):
            if parameters[x].valueAsText:
                open(temp.name, "a").write(parameters[x].valueAsText + '\n')
            else:
                open(temp.name, "a").write('\n')
            
        temp.close()
        
        """Parse the parameters for GeoExpress."""
        metadata_string = getGXVersion() + ' -i "' + parameters[0].valueAsText + '" -o "' + parameters[1].valueAsText + \
            '" -metadatafile "' + temp.name + '"'
        
        """If you specify a compression ratio, append it to the command."""
        if parameters[-1].valueAsText:
            metadata_string = metadata_string + ' -cr ' + parameters[-1].valueAsText
            
        subprocess.call(metadata_string, shell=False)
        os.remove(temp.name)
        return
        
class Reproject(object):
    def __init__(self):
        """Reprojection Tool."""
        self.label = "Reproject Tool"
        self.description = "Enter an EPSG code for the source image and an EPSG code for the output image."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions."""
        in_file = arcpy.Parameter(
			displayName = "Input File",
			name = "in_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Input")
        
        out_file = arcpy.Parameter(
			displayName = "Output File",
			name = "out_file",
			datatype = "File",
			parameterType = "Required",
			direction = "Output")
            
        in_EPSG = arcpy.Parameter(
			displayName = "Source EPSG",
			name = "in_EPSG",
			datatype = "String",
			parameterType = "Required",
			direction = "Input")
            
        out_EPSG = arcpy.Parameter(
			displayName = "Output EPSG",
			name = "out_EPSG",
			datatype = "String",
			parameterType = "Required",
			direction = "Input")
        
        compression_ratio = arcpy.Parameter(
			displayName = "Compression Ratio",
			name = "compression_ratio",
			datatype = "String",
			parameterType = "Optional",
			direction = "Input")
              
        params = [in_file, out_file, in_EPSG, out_EPSG, compression_ratio]
        return params

    def updateMessages(self, parameters):
        """Compression Ratio must be a whole number greater than 0."""
        err_not_number = "The compression ratio must be a whole number."
        err_negative_value = "The compression ratio cannot be a negative number."
        compression_ratio = parameters[-1].valueAsText
        
        if compression_ratio:
            try:
                int(compression_ratio)
                if int(compression_ratio) < 0:
                    parameters[-1].setErrorMessage(err_negative_value)
            except ValueError:
                parameters[-1].setErrorMessage(err_not_number)
                
        return 
    
    def execute(self, parameters, messages):
        """Parse the parameters for GeoExpress."""
        reproject_string = getGXVersion() + ' -i "' + parameters[0].valueAsText + '" -o "' + parameters[1].valueAsText + \
            '" -fromepsg ' + parameters[2].valueAsText + ' -toepsg ' + parameters[3].valueAsText
        
        """If you specify a compression ratio, append it to the command."""
        if parameters[-1].valueAsText:
            reproject_string = reproject_string + ' -cr ' + parameters[-1].valueAsText
            
        subprocess.call(reproject_string, shell=False)
        return
