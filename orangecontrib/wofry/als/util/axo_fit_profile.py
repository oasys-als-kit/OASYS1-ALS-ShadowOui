import numpy
from srxraylib.plot.gol import plot_table, plot

from orangecontrib.wofry.als.util.axo import orthonormalize_a, linear_2dgsfit1, linear_basis

def calculate_orthonormal_basis(file_influence_functions="",
                                file_orthonormal_functions="",
                                mask=None,
                                do_plot=True,):

    input_array = numpy.loadtxt(file_influence_functions)
    # prepare input format for orthonormalize_a
    col19 = input_array[:, 0].copy() * 0 + 1
    col20 = numpy.linspace(-1, 1, input_array.shape[0])

    a = []
    a.append({'a': col19, 'total_squared': 0})
    a.append({'a': col20, 'total_squared': 0})
    for i in [9, 10, 8, 11, 7, 12, 6, 13, 5, 14, 4, 15, 3, 16, 2, 17, 1, 18]:
        a.append({'a': input_array[:, i], 'total_squared': 0})

    if do_plot:
        abscissas = input_array[:, 0].copy()
        plot_table(abscissas, input_array[:, 1:].T, title="influence functions")

    # compute the basis
    b, matrix = orthonormalize_a(a, mask=mask)

    # plot basis
    b_array = numpy.zeros((input_array.shape[0], 20))

    for i in range(20):
        b_array[:, i] = b[i]["a"]

    if do_plot:
        plot_table(abscissas, b_array.T, title="basis functions")

    if file_orthonormal_functions != "":
        numpy.savetxt(file_orthonormal_functions , b_array)
        print("File written to disk %s " % file_orthonormal_functions)

def axo_fit_profile(filein, fileout="",
                    file_influence_functions="",
                    file_orthonormal_functions="",
                    calculate=False,
                    mask=None):

    from srxraylib.plot.gol import plot, plot_table

    # loads file with data to fit
    input_array = numpy.loadtxt(file_influence_functions)

    abscissas = input_array[:, 0].copy()
    print("abscisas: ", abscissas)

    tmp = numpy.loadtxt(filein)

    # plot(tmp[:, 0], tmp[:, 1], title="data to fit")
    u = numpy.interp(abscissas, 1000 * tmp[:, 0], tmp[:, 1])
    # plot(abscissas, u, title="Result of fit")

    if calculate:
        calculate_orthonormal_basis(file_influence_functions=file_influence_functions,
                                    file_orthonormal_functions=file_orthonormal_functions,
                                    mask=None,
                                    do_plot=False, )

    b_array = numpy.loadtxt(file_orthonormal_functions)

    b = []
    for i in range(b_array.shape[1]):
        b.append({'a': b_array[:, i], 'total_squared':(b_array[:, i]**2).sum()})

    # perform the fit
    v = linear_2dgsfit1(u, b, mask=mask)
    print("coefficients: ",v)

    # evaluate the fitted data form coefficients and basis
    y = linear_basis(v, b)


    if fileout != "":
        f = open(fileout,'w')
        for i in range(abscissas.size):
            f.write("%g  %g \n"%(1e-3*abscissas[i],y[i]))
        f.close()
        print("File %s written to disk"%fileout)

    return v, abscissas, u, y # coeffs, abscisas, input interpolated, fit

if __name__ == "__main__":
    import os

    do_plot = True


    file_influence_functions = os.path.join("data","aps_axo_influence_functions2019.dat")  # abscissas in mm!!
    file_orthonormal_functions = os.path.join("data","aps_axo_orthonormal_functions2019.dat")

    filein = "C:/Users/Manuel/OASYS1.2/ML_Optics/oasys_scripts/correction.dat"
    fileout = ""

    v, abscissas, u, y = axo_fit_profile(filein,
                                         fileout=fileout,
                                         file_influence_functions=file_influence_functions,
                                         file_orthonormal_functions=file_orthonormal_functions,
                                         calculate=False)

    print("Coefficients of the orthonormal basis: ")
    v_labels = []
    for i in range(v.size):
        v_labels.append("v[%d]" % i)
        print("v[%d] = %5.2f nm" % (i, 1e9 * v[i]))


    if do_plot:
        tmp = numpy.loadtxt(filein)
        plot(tmp[:, 0], tmp[:, 1], title="data to fit", xtitle="x[m]", ytitle="y [m]")
        # plot(abscissas, u, title="Result of fit")
        plot(abscissas,u,abscissas,y,
             legend=["Data interpolated","Fit"],
             title=v, xtitle="x[mm]", ytitle="y[m]")
        plot(1e3*tmp[:, 0], tmp[:, 1],
             abscissas, y,
             legend=["Data", "Fit"], xtitle="x[mm]", ytitle="y [m]",title=v)



        import matplotlib.pyplot as plt; plt.rcdefaults()
        import numpy as np
        import matplotlib.pyplot as plt

        y_pos = np.arange(v.size)

        plt.bar(y_pos, v, align='center', alpha=0.5)
        plt.xticks(y_pos, v_labels)
        plt.ylabel('Usage')
        plt.title('Coefficients in ')

        plt.show()


    # import orangecanvas.resources as resources
    # dir = resources.package_dirname("orangecontrib.wofry.als.util")
    # file1 = os.path.join(dir, file_influence_functions)
    # print(">>>>>>>>>>>>>>",file1)