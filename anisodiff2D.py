import numpy as np
from scipy.ndimage import convolve
from math import sqrt

def anisodiff2D(im, num_iter, delta_t, kappa, option):
    """ANISODIFF2D Conventional anisotropic diffusion.
    
    DIFF_IM = ANISODIFF2D(IM, NUM_ITER, DELTA_T, KAPPA, OPTION) perfoms 
    conventional anisotropic diffusion (Perona & Malik) upon a gray scale
    image. A 2D network structure of 8 neighboring nodes is considered for 
    diffusion conduction.

    ARGUMENT DESCRIPTION:
          IM       - gray scale image (MxN).
          NUM_ITER - number of iterations. 
          DELTA_T  - integration constant (0 <= delta_t <= 1/7).
                     Usually, due to numerical stability this 
                     parameter is set to its maximum value.
          KAPPA    - gradient modulus threshold that controls the conduction.
          OPTION   - conduction coefficient functions proposed by Perona & Malik:
                     1 - c(x,y,t) = exp(-(nablaI/kappa)**2),
                         privileges high-contrast edges over low-contrast ones. 
                     2 - c(x,y,t) = 1./(1 + (nablaI/kappa)**2),
                         privileges wide regions over smaller ones. 

    OUTPUT DESCRIPTION:
           DIFF_IM - (diffused) image with the largest scale-space parameter.

    Example
    -------------
    s = phantom(512) + randn(512);
    num_iter = 15;
    delta_t = 1/7;
    kappa = 30;
    option = 2;
    ad = anisodiff2D(s,num_iter,delta_t,kappa,option);
    figure, subplot 121, imshow(s,[]), subplot 122, imshow(ad,[])

    See also anisodiff1D, anisodiff3D.

    References: 
    P. Perona and J. Malik. 
    Scale-Space and Edge Detection Using Anisotropic Diffusion.
    IEEE Transactions on Pattern Analysis and Machine Intelligence, 
    12(7):629-639, July 1990.

    G. Grieg, O. Kubler, R. Kikinis, and F. A. Jolesz.
    Nonlinear Anisotropic Filtering of MRI Data.
    IEEE Transactions on Medical Imaging,
    11(2):221-232, June 1992.

    MATLAB implementation based on Peter Kovesi's anisodiff(.):
    P. D. Kovesi. MATLAB and Octave Functions for Computer Vision and Image Processing.
    School of Computer Science & Software Engineering,
    The University of Western Australia. Available from:
    <http://www.csse.uwa.edu.au/~pk/research/matlabfns/>.

    Credits:
    Daniel Simoes Lopes
    ICIST
    Instituto Superior Tecnico - Universidade Tecnica de Lisboa
    danlopes (at) civil ist utl pt
    http://www.civil.ist.utl.pt/~danlopes

    May 2007 original version.
    """

    # Convert input image to double.
    im = np.float64(im);

    # PDE (partial differential equation) initial condition.
    diff_im = im.copy();

    # Center pixel distances.
    dx = 1;
    dy = 1;
    dd = sqrt(2);

    # 2D convolution masks - finite differences.
    hN = np.array([[0, 1, 0],[0, -1, 0],[0, 0, 0]])
    hS = np.array([[0, 0, 0],[0, -1, 0],[0, 1, 0]])
    hE = np.array([[0, 0, 0],[0, -1, 1],[0, 0, 0]])
    hW = np.array([[0, 0, 0],[1, -1, 0],[0, 0, 0]])
    hNE = np.array([[0, 0, 1],[0, -1, 0],[0, 0, 0]])
    hSE = np.array([[0, 0, 0],[0, -1, 0],[0, 0, 1]])
    hSW = np.array([[0, 0, 0],[0, -1, 0],[1, 0, 0]])
    hNW = np.array([[1, 0, 0],[0, -1, 0],[0, 0, 0]])

    # Anisotropic diffusion.
    for t in range(num_iter):

        # Finite differences. 
        nablaN = convolve(diff_im,hN);
        nablaS = convolve(diff_im,hS);   
        nablaW = convolve(diff_im,hW);
        nablaE = convolve(diff_im,hE);   
        nablaNE = convolve(diff_im,hNE);
        nablaSE = convolve(diff_im,hSE);   
        nablaSW = convolve(diff_im,hSW);
        nablaNW = convolve(diff_im,hNW); 
        
        # Diffusion function.
        if option == 1:
            cN = np.exp(-(nablaN/kappa)**2);
            cS = np.exp(-(nablaS/kappa)**2);
            cW = np.exp(-(nablaW/kappa)**2);
            cE = np.exp(-(nablaE/kappa)**2);
            cNE = np.exp(-(nablaNE/kappa)**2);
            cSE = np.exp(-(nablaSE/kappa)**2);
            cSW = np.exp(-(nablaSW/kappa)**2);
            cNW = np.exp(-(nablaNW/kappa)**2);
        elif option == 2:
            cN = 1./(1 + (nablaN/kappa)**2);
            cS = 1./(1 + (nablaS/kappa)**2);
            cW = 1./(1 + (nablaW/kappa)**2);
            cE = 1./(1 + (nablaE/kappa)**2);
            cNE = 1./(1 + (nablaNE/kappa)**2);
            cSE = 1./(1 + (nablaSE/kappa)**2);
            cSW = 1./(1 + (nablaSW/kappa)**2);
            cNW = 1./(1 + (nablaNW/kappa)**2);

        # Discrete PDE solution.
        diff_im += \
              delta_t*( \
                  (1/(dy**2))*cN*nablaN + (1/(dy**2))*cS*nablaS + \
                  (1/(dx**2))*cW*nablaW + (1/(dx**2))*cE*nablaE + \
                  (1/(dd**2))*cNE*nablaNE + (1/(dd**2))*cSE*nablaSE + \
                  (1/(dd**2))*cSW*nablaSW + (1/(dd**2))*cNW*nablaNW );
           
        # Iteration warning.
        print('\rIteration {0}\n'.format(t));
    return diff_im
