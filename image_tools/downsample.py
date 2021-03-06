import numpy
try:
    from scipy.stats import nanmean as mean
except ImportError:
    from numpy import nanmean as mean
except ImportError:
    from numpy import mean

def downsample(myarr,factor,estimator=mean):
    """
    Downsample a 2D array by averaging over *factor* pixels in each axis.
    Crops upper edge if the shape is not a multiple of factor.

    This code is pure numpy and should be fast.

    keywords:
        estimator - default to mean.  You can downsample by summing or
            something else if you want a different estimator
            (e.g., downsampling error: you want to sum & divide by sqrt(n))
    """
    ys,xs = myarr.shape
    crarr = myarr[:ys-(ys % int(factor)),:xs-(xs % int(factor))]
    dsarr = estimator( numpy.concatenate([[crarr[i::factor,j::factor] 
        for i in range(factor)] 
        for j in range(factor)]), axis=0)
    return dsarr

def downsample_cube(myarr,factor,ignoredim=0):
    """
    Downsample a 3D array by averaging over *factor* pixels on the last two
    axes.
    """
    if ignoredim > 0: myarr = myarr.swapaxes(0,ignoredim)
    zs,ys,xs = myarr.shape
    crarr = myarr[:,:ys-(ys % int(factor)),:xs-(xs % int(factor))]
    dsarr = mean(numpy.concatenate([[crarr[:,i::factor,j::factor] 
        for i in range(factor)] 
        for j in range(factor)]), axis=0)
    if ignoredim > 0: dsarr = dsarr.swapaxes(0,ignoredim)
    return dsarr

def downsample_1d(myarr,factor,estimator=mean):
    """
    Downsample a 1D array by averaging over *factor* pixels.
    Crops right side if the shape is not a multiple of factor.

    This code is pure numpy and should be fast.

    keywords:
        estimator - default to mean.  You can downsample by summing or
            something else if you want a different estimator
            (e.g., downsampling error: you want to sum & divide by sqrt(n))
    """
    xs = myarr.size
    crarr = myarr[:xs-(xs % int(factor))]
    dsarr = estimator( numpy.concatenate([[crarr[i::factor] 
        for i in range(factor)] ]),axis=0)
    return dsarr

try:
    def downsample_axis(myarr, factor, axis, estimator=numpy.nanmean, truncate=False):
        """
        Downsample an ND array by averaging over *factor* pixels along an axis.
        Crops right side if the shape is not a multiple of factor.

        This code is pure np and should be fast.

        Parameters
        ----------
        myarr : `~numpy.ndarray`
            The array to downsample
        factor : int
            The factor to downsample by
        axis : int
            The axis to downsample along
        estimator : function
            defaults to mean.  You can downsample by summing or
            something else if you want a different estimator
            (e.g., downsampling error: you want to sum & divide by sqrt(n))
        truncate : bool
            Whether to truncate the last chunk or average over a smaller number.
            e.g., if you downsample [1,2,3,4] by a factor of 3, you could get either
            [2] or [2,4] if truncate is True or False, respectively.
        """
        # size of the dimension of interest
        xs = myarr.shape[axis]
        
        if xs % int(factor) != 0:
            if truncate:
                view = [slice(None) for ii in range(myarr.ndim)]
                view[axis] = slice(None,xs-(xs % int(factor)))
                crarr = myarr[view]
            else:
                newshape = list(myarr.shape)
                newshape[axis] = (factor - xs % int(factor))
                extension = numpy.empty(newshape) * numpy.nan
                crarr = numpy.concatenate((myarr,extension), axis=axis)
        else:
            crarr = myarr

        def makeslice(startpoint,axis=axis,step=factor):
            # make empty slices
            view = [slice(None) for ii in range(myarr.ndim)]
            # then fill the appropriate slice
            view[axis] = slice(startpoint,None,step)
            return view

        # The extra braces here are crucial: We're adding an extra dimension so we
        # can average across it!
        stacked_array = numpy.concatenate([[crarr[makeslice(ii)]] for ii in range(factor)])

        dsarr = estimator(stacked_array, axis=0)
        return dsarr
except AttributeError:
    import warnings
    warnings.warn("Numpy doesn't have a nanmean attribute; a more recent version of numpy is required.")

    def downsample_axis(*args, **kwargs):
        raise AttributeError("This version of numpy doesn't possess a nanmean.")
