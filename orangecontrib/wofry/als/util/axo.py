
import numpy
import os

# function orthonormalize_a, a, mask=mask, matrix=matrix
def orthonormalize_a( a, mask=None):
    """
     (c) Kenneth A. Goldberg  http://goldberg.lbl.gov  KAGoldberg(at)lbl.gov
     Lawrence Berkeley National Laboratory
     1/3/20
     IDL files: orthonormalize_a.pro


    --- a has to be defined like this
        in IDL: a = replicate({a:x, total_squared:0d}, Nz+1)

        in python: a = [{"a":x, "total_squared":0}] * (Nz+1)

    --- This function was written to orthonormalize the APS AXO data influence functions on 2020-01-03,
        but it is general and can orthonormalize any-dimensional basis functions with or without weighting

        The input argument, a, is a structure variable defined like this example
           a = replicate({a:dblarr(500), total_squared:0d}, 38)
        In this way, we access a[0].a, a[1].a, a[2].a as basis functions.
        In the original intention of this routine, a[i].a will contain the influence functions
          from the APS AXO mirror (measured in October 2019). The basis functions of a[i].a are
          not necessarily orthogonal or orthonormal.
        To facilitate fitting, we add a constant a[i].a = 1, and a linear term a[i].a = x,
          to the basis.

       The optional 'mask' keyword is a user-supplied weighting function.
       It should have the same dimensions as a[i].a .
       If mask is not given, we assume uniform weighting across the domain.

       The 'matrix' keyword returns a NxN transformation matrix from the input basis, a,
         to the output basis, b.

       2020-01-27, I changed the normalization so that
       total(mask*b[i].a^2) = 1.0 for all i

    :param a:
    :param mask:
    :return:
    """

    #   b = a  ;--- copy so it's the same size as the original. b becomes the output, the orthonormal basis.
    b = a.copy()


    #   Nz = n_elements(a)-1
    #   matrix = dblarr(Nz+1, Nz+1)  ;--- this will be returned in the keyword
    Nz = len(a)-1
    matrix = numpy.zeros((Nz+1,Nz+1))


    if mask is not None:
        #
        #   if isa(mask) then begin  ;--- do this code if there is a mask
        #
        #       ;--- This is a Gram-Schmidt process
        #       ;    One by one, each new elements is projected onto the existing basis and made orthogonal.
        #     for i=1,Nz do begin
        #       for j=0,i-1 do begin
        #         matrix[i,j] = (total(mask * b[i].a * b[j].a, /double) / total( mask * b[j].a^2, /double ))
        #         b[i].a -= b[j].a * matrix[i,j]
        #       endfor
        #       b[i].a /= sqrt(total(mask * b[i].a^2, /double))  ;--- normalize each element to rms = 1.0
        #     endfor
        #
        for i in range(1,Nz+1):
            for j in range(i):
                matrix[i, j] = ((mask * b[i]["a"] * b[j]["a"]).sum() / (mask * b[j]["a"] ** 2).sum() )
                b[i]["a"] -= b[j]["a"] * matrix[i, j]
            b[i]["a"] /= numpy.sqrt(numpy.sum(mask * b[i]["a"] ** 2))  #--- normalize each element to rms = 1.0

        #       ;--- compute and store the total_squared for each. We use this in future normalization to save time
        #     for i=0,Nz do $
        #       b[i].total_squared = total( mask * b[i].a^2, /double )  ;--- must be 1.0
        #
            for i in range(Nz+1):
                b[i]["total_squared"] = numpy.sum( mask * b[i]["a"] ** 2)  #--- must be 1.0


        #   endif else begin   ;--- do this code below if there is no mask

    else:
        #       ;--- This is a Gram-Schmidt process
        #       ;    One by one, each new elements is projected onto the existing basis and made orthogonal.

        #     for i=1,Nz do begin
        #       for j=0,i-1 do begin
        #         matrix[i,j] = (total(b[i].a * b[j].a, /double) / total( b[j].a^2, /double ))
        #         b[i].a -= b[j].a * matrix[i,j]
        #       endfor
        #       b[i].a /= sqrt(total(b[i].a^2, /double ))  ;--- normalize each element to rms = 1.0
        #     endfor

        for i in range(1,Nz+1):
            for j in range(i):
                matrix[i, j] = (       (b[i]["a"] * b[j]["a"]).sum() / (b[j]["a"] ** 2).sum() )
                b[i]["a"] -= b[j]["a"] * matrix[i, j]
            b[i]["a"] /= numpy.sqrt(numpy.sum(b[i]["a"] ** 2))  #--- normalize each element to rms = 1.0


        #       ;--- compute and store the total_squared for each. We use this in future normalization to save time

        #     for i=0,Nz do $
        #       b[i].total_squared = total( b[i].a^2, /double )  ;--- must be 1.0
        #   endelse
        for i in range(Nz+1):
            b[i]["total_squared"] = numpy.sum( b[i]["a"] ** 2)  #--- must be 1.0

    # return, b  ;--- return the structure containing the basis.
    # end
    return (b, matrix)




# function linear_2dgsfit1, u, b, Nz=Nz, mask=mask
def linear_2dgsfit1(u, b, Nz=None, mask=None):
    """
    # ; (c) Kenneth A. Goldberg  http://goldberg.lbl.gov  KAGoldberg(at)lbl.gov
    # ; Lawrence Berkeley National Laboratory
    # ; 09/05/2011, based on linear_gsfit1.pro
    # ; IDL files: linear_2dgsfit1.pro
    # ;
    # ;  u are the values we want to fit (the target array)
    # ;    on the same domain as b[i].a
    # ;
    # ; b = linear_2dpolynomials1(N, Ny=Ny, Nz=12, /double)  ;--- create the basis. Ny is the optional domain width
    # ; v = linear_2dgsfit1(wavefront, b, Nz=8)              ;--- fit a wavefront to 8+1 polynomials (order 8)
    # ; wf_fit = linear_basis1(v, b)                         ;--- show the fit wavefront phase
    # ;
    # ; 09/05/2011 created this to handle rectangular apertures, but general enough that
    # ; it should work with any orthogonal polynomials.
    #
    # ; u is an array that you want to fit to the basis, b
    # ; b is the structure containing the basis polynomials.
    # ; NZ can be inferred from the size of b, or specified by the user. It's the # of fitting terms.
    # ; mask is a point-by-point weighting with the same size as u
    # ;
    # ; IMPORTANT: Never switch from using a mask to not using a mask with the same basis functions.
    # ;    Orthogonalization is performed USING the mask if it's present, or not. So be consistent.
    # ; IMPORTANT: input array u, b[i].a basis functions, and mask must all be of the same array size
    # ;
    # ; Note, the scalar values b[i].total_squared are calculated in the orthonormalization.
    # ;   When the polynomials are orthonormal, total_squared is 1.0 by definition.
    # ;   When they are merely orthogonal, they take a positive-definite value.
    # ;   They are calculated with  b[i].total_squared = total( mask * b[i].a^2, /double ), or
    # ;     b[i].total_squared = total( b[i].a^2, /double )  depending on whether or not a mask (weighting)
    # ;     is being used.
    # ;
    """

    #
    #     ;--- Either use a user-specified Nz, or infer it from the number of basis functions in the structure, b
    #     ;    Make sure we don't exceed the number of basis functions.

    #   Nz = (defined(Nz) ? Nz : n_elements(b) ) < n_elements(b)
    if Nz is None:
        Nz = len(b)


    #
    #     ;--- This will be the vector of fit coefficients. Use Nz+1 output terms by convnetion.
    #     ;    Calculations will be double or single precision based on the type of b[i].a
    #     ;

    #   v = (size(b[0].a, /type) EQ 5) ? dblarr(Nz) : fltarr(Nz)   ;--- output vector of coefficients
    v = numpy.zeros(Nz)


    #
    #   if defined(mask) then begin   ;--- Use the mask weighting function.
    #
    #     for i=0,Nz-1 do $           ;    Project onto the basis, normalize properly
    #       v[i] = total(mask * u * b[i].a) / b[i].total_squared  ;--- here, total_squared respects the mask
    #
    #   endif else begin              ;--- Use no mask weighting function.
    #
    #     for i=0,Nz-1 do $           ;    Project onto the basis, normalize properly
    #       v[i] = total(u * b[i].a) / b[i].total_squared
    #
    #   endelse
    #
    if mask is not None:
        for i in range(Nz): # ;    Project onto the basis, normalize properly
            v[i] = numpy.sum(mask * u * b[i]["a"]) / b[i]["total_squared"]  #;--- here, total_squared respects the mask
    else:
        for i in range(Nz): # ;--- Use no mask weighting function.
            v[i] = numpy.sum(u * b[i]["a"]) / b[i]["total_squared"]  #;--- here, total_squared respects the mask

    # return, v  ;--- return the output coefficients in a vector of size Nz+1
    # end
    return v


#function linear_basis1, v, b
def linear_basis(v, b):
    """
    #; (c) Kenneth A. Goldberg  http://goldberg.lbl.gov  KAGoldberg(at)lbl.gov
    #; Lawrence Berkeley National Laboratory
    #; 8/03/09
    #; IDL files: linear_basis1.pro
    #
    #; When the linear polynomial basis functions, b[i].a, are already calculated,
    #; using linear_polynomials1.pro, or a similar routine, we can calculate an output vector
    #; from an input set of coefficients, v
    #;
    #; b = linear_polynomials1(N, Nz=12, /double)  ;--- create the basis
    #; v = linear_gsfit1(wavefront, b, Nz=8)       ;--- fit a wavefront to 8 polynomials
    #; wf_fit = linear_basis1(v, b)                ;--- show the fit wavefront phase
    #;
    #; v is a vector of coefficients
    #; b is a structure containing the basis functions
    #; This routine does not worry about the size of the arrays

    :param v:
    :param b:
    :return:
    """



    #
    #    ;--- Create an output array filled with zeros to start
    #    ;    The array will be single or double precision depending on the basis function type.
    #    ;
    #  y = b[0].a * 0
    y = numpy.zeros_like( b[0]["a"] )

    #
    #    ;--- If the vector is too long, complain, but don't fail
    #  if n_elements(v) GT n_elements(b) $
    #    then message, 'Mismatch between the number of coefficients and number of polynomials', /INFORMATIONAL
    #

    v = numpy.array(v) # if list, convert IT to numpy.array
    if v.size > len(b):
        raise Exception("'Mismatch between the number of coefficients and number of polynomials'")

    #    ;--- choose an output number of elements N that does not exceed the number of basis functions
    #  N = n_elements(v) < n_elements(b)
    N = min([ v.size, len(b)])

    #    ;--- Add up the vectors. We use a for loop because the basis functions are contained
    #    ;    in a structure making it hard to create a giant matric multiplication.
    #    ;

    #  for i=0,N-1 do $
    #    if (v[i] NE 0.) then y += v[i] * b[i].a   ;--- we skip zeros to save time.
    for i in range(N):
        if (v[i] != 0.):
            y += v[i] * b[i]["a"] #;--- we skip zeros to save time.

    #return, y  ;--- the output array will have the same size as b[i].a elements
    #end
    return y


if __name__ == "__main__":

    from srxraylib.plot.gol import plot, plot_table


    input_array = numpy.loadtxt(os.path.join("data","aps_axo_influence_functions2019.dat"))

    abscissas = input_array[:,0].copy()
    print("abscisas: ",abscissas)

    # prepare input format for orthonormalize_a
    col19 = input_array[:, 0].copy() * 0 + 1
    col20 = numpy.linspace(-1,1,input_array.shape[0])

    a = []
    a.append({'a': col19, 'total_squared': 0})
    a.append({'a': col20, 'total_squared': 0})
    for i in [9, 10, 8, 11, 7, 12, 6, 13, 5, 14, 4, 15, 3, 16, 2, 17, 1, 18]:
        a.append({'a': input_array[:, i], 'total_squared':0})

    plot_table(abscissas, input_array[:, 1:].T, title="influence functions")

    # prepare a Gaussian (data to fit)
    sigma = (abscissas[-1] - abscissas[0])
    u = 15 * numpy.exp( - abscissas**2 / 2 / sigma)

    mask = None # u


    # compute the basis
    b, matrix = orthonormalize_a(a, mask=mask)

    print(">>>>> matrix", matrix.shape)

    # plot basis
    b_array = numpy.zeros((input_array.shape[0],20))

    for i in range(20):
        b_array[:,i] = b[i]["a"]
    plot_table(abscissas, b_array.T, title="basis functions")


    # perform the fit
    v = linear_2dgsfit1(u, b, mask=mask)
    print("coefficients for orthonormal basis: ",v)

    vinfl = numpy.dot(matrix,v)

    print(matrix)
    print("coefficients for influence functions basis: ", vinfl.shape,vinfl)



    # evaluate the fitted data form coefficients and basis
    y = linear_basis(v, b)

    # evaluate the fitted data form coefficients and basis
    yinfl = linear_basis(vinfl, a)

    plot(abscissas, u, abscissas, y,legend=["Data", "Fit (orthonormal)"])
    # plot(abscissas,u,abscissas,y,abscissas,yinfl,legend=["Data","Fit (orthonormal)","Fit (sorted influence)"])