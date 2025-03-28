#######################################################################
# Viktor Y. D. Sumida e-mail: viktorsumida@icloud.com                  #
# PhD student in Astrophysics at Mackenzie University                  #
# Contact via e-mail: viktorsumida@icloud.com                            #
#######################################################################

import numpy as np
import pandas as pd
from matplotlib import pyplot
from star import Star
from eclipse_nv1 import Eclipse
from Planeta import Planeta
from verify import Validar, ValidarEscolha, calSemiEixo, calculaLat
import os

h_Planck = 6.626e-34
c_Light = 2.998e+8
k_Boltzmann = 1.38e-23

def planck(wavelength, Temp):
    aux = h_Planck * c_Light / (wavelength * k_Boltzmann * Temp)
    intensity = (2 * h_Planck * (c_Light**2)) / ((wavelength**5) * (np.exp(aux) - 1.0))
    return intensity

# Variáveis globais para armazenar o baseline em memória
BASELINE_WAVE = None
BASELINE_DLAMDA = None

class MainProgram:

    def __init__(self, *, target, num_elements, profile, c1, c2, c3, c4, lambdaEff, raio, 
                 intensidadeMaxima, tamanhoMatriz, raioStar, ecc, anom, tempStar, starspots, 
                 quantidade, lat, longt, r, semiEixoUA, massStar, plot_anim, periodo, 
                 anguloInclinacao, raioPlanetaRj, plot_graph, plot_star, 
                 tempSpot):
        self.target = target
        self.num_elements = num_elements
        self.profile = profile
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.c4 = c4
        self.lambdaEff = lambdaEff
        self.raio = raio
        self.intensidadeMaxima = intensidadeMaxima
        self.tamanhoMatriz = tamanhoMatriz
        self.raioStar = raioStar
        self.ecc = ecc
        self.anom = anom
        self.tempStar = tempStar
        self.starspots = starspots
        self.quantidade = quantidade
        # Mantenha lat e longt como arrays para suportar múltiplas manchas
        self.lat = lat
        self.longt = longt
        self.r = r
        self.semiEixoUA = semiEixoUA
        self.massStar = massStar
        self.plot_anim = plot_anim
        self.periodo = periodo
        self.anguloInclinacao = anguloInclinacao
        self.raioPlanetaRj = raioPlanetaRj
        self.plot_graph = plot_graph
        self.plot_star = plot_star
        self.tempSpot = tempSpot

        raioSun = self.raioStar
        raioStar = self.raioStar * 696340  # converting from solar radii to km
    
        # Cria a estrela
        lambdaEfetivo = (0.0028976 / self.tempStar)
        intensidadeEstrelaLambdaMaximo = planck(lambdaEfetivo, self.tempStar)

        raioPlanJup = self.raioPlanetaRj

        print('stellar effective temperature:', self.tempStar)
        print('active region effective temperature:', self.tempSpot)

        intensidadeMancha = np.zeros(self.num_elements)
        intensidadeManchaNormalizada = np.zeros(self.num_elements)
        intensidadeManchaRazao = np.zeros(self.num_elements)

        epsilon_Rackham = [0 for j in range(self.num_elements)]

        # Remova a conversão de lat e longt para float, mantendo-os como arrays:
        # self.r já é um escalar e não precisa ser modificado.
        
        massPlaneta = 0  # EXCALIBUR does not handle planet mass
        planeta_ = Planeta(self.semiEixoUA, raioPlanJup, self.periodo, 
                           self.anguloInclinacao, self.ecc, self.anom, 
                           raioStar, massPlaneta)

        stack_curvaLuz = None
        stack_tempoHoras = None
        
        semiEixoRaioStar = ((1.469*(10**8))*semiEixoUA)/raioStar
        latsugerida = calculaLat(semiEixoRaioStar,anguloInclinacao)
        print("The suggested latitude for the spot to influence the star's light curve is:", latsugerida)

        count3 = 0
        while count3 < self.num_elements:
            #print(f"Starting iteration {count3+1}")
            print('Starting the simulation ' + str(count3 + 1) + ' of ' + str(self.num_elements))
            
            intensidadeEstrelaLambda = planck(self.lambdaEff[count3] * 1.0e-6, self.tempStar)
            intensidadeEstrelaLambdaNormalizada = (
                float(self.intensidadeMaxima) 
                * intensidadeEstrelaLambda 
                / intensidadeEstrelaLambdaMaximo
            )
            Nx = self.tamanhoMatriz
            Ny = self.tamanhoMatriz

            estrela_ = Star(self.raio, raioSun, intensidadeEstrelaLambdaNormalizada,
                               self.c1[count3], self.c2[count3],
                               self.c3[count3], self.c4[count3], self.tamanhoMatriz)
            
            estrela_.resetManchas()
            
            if starspots == False:
                # spotless star
                print('Spotless star created')
                estrela_matriz = estrela_.getMatrizEstrela()
                
            elif starspots == True:
                
                mancha = [None] * self.quantidade
                
                intensidadeMancha[count3] = planck(self.lambdaEff[count3] * 1.0e-6, self.tempSpot)
                intensidadeManchaNormalizada[count3] = (
                    intensidadeMancha[count3] 
                    * intensidadeEstrelaLambdaNormalizada 
                    / intensidadeEstrelaLambda
                )
                intensidadeManchaRazao[count3] = (
                    intensidadeManchaNormalizada[count3] 
                    / intensidadeEstrelaLambdaNormalizada
                )
                count2 = 0
                while count2 < self.quantidade:
                    # Usa os valores individuais de lat e longt para cada mancha
                    mancha[count2] = Star.Mancha(intensidadeManchaRazao[count3],
                                                    self.r, self.lat[count2], self.longt[count2])
                    raioMancha = self.r * raioStar
                    area = np.pi * (raioMancha ** 2)
                    # print('Number of spots:', self.quantidade)
                    # print('each spot radius:', self.r)
                    # print('spot radius (sum):', self.r * quantidade)
                    # print('each spot coverage area ff (sum):', self.r ** 2)
                    # print('spot coverage area ff (sum):', (self.r ** 2) * quantidade)

                    estrela_.addMancha(mancha[count2])
                    count2 += 1
                    
                estrela_.criaEstrelaManchada()
                estrela_matriz = estrela_.getMatrizEstrela()
                
            if self.plot_star == True:
                estrela_.Plotar(self.tamanhoMatriz, estrela_.getMatrizEstrela())

            # Cálculo do fator epsilon com melhor estruturação
            filling_factor = self.quantidade * (self.r ** 2)  # Definição do filling factor
            #print("MAIN quantidade de manchas: ", self.quantidade)
            #print("MAIN raio de cada mancha: ", self.r)
            #print("MAIN filling factor total: ", filling_factor)
            intensity_ratio = 1 - intensidadeManchaRazao[count3]  # Razão de intensidade
            # Evita divisão por zero
            denominator = 1 - (filling_factor * intensity_ratio)
            if denominator == 0:
                raise ValueError("Denominator became zero, leading to a division error.")
            fatorEpsilon = 1 / denominator
            epsilon_Rackham[count3] = fatorEpsilon
            #print('Epsilon factor (Rackham):', fatorEpsilon)

            # Eclipse (sem CME ou luas)
            eclipse_ = Eclipse(Nx, Ny, self.raio, estrela_, planeta_)
            eclipse_.setEstrela(estrela_matriz)
            eclipse_.criarEclipse(self.plot_anim, self.plot_graph)

            tempoHoras = 1
            eclipse_.geraTempoHoras(tempoHoras)

            tempoTransito = eclipse_.getTempoTransito()
            curvaLuz = eclipse_.getCurvaLuz()
            tempoHoras = eclipse_.getTempoHoras()

            if count3 == 0:
                tamanho_curva = len(curvaLuz)
                tamanho_tempo = len(tempoHoras)
                stack_curvaLuz = np.zeros((self.num_elements, tamanho_curva))
                stack_tempoHoras = np.zeros((self.num_elements, tamanho_tempo))

            stack_curvaLuz[count3, :] = eclipse_.getCurvaLuz()
            stack_tempoHoras[count3, :] = eclipse_.getTempoHoras()

            count3 += 1
            #print(f"Finishing iteration {count3}")

        ############################################################################################
        # Plotting the light curves
        ############################################################################################
        lambdaEff_nm = [0.] * self.num_elements
        D_lambda = [0.] * self.num_elements
        count4 = 0

        palette = pyplot.cm.cool_r(np.linspace(0, 1, self.num_elements))
        count_palette = self.num_elements - 1
        pyplot.rcParams['axes.grid'] = False
        pyplot.rcParams['axes.edgecolor'] = 'black'

        while count4 < self.num_elements:
            lambdaEff_nm[count4] = self.lambdaEff[count4] * 1000
            pyplot.plot(
                stack_tempoHoras[count4],
                stack_curvaLuz[count4],
                label=int(lambdaEff_nm[count4]),
                color=palette[count_palette],
                linewidth=1.5
            )

            index_midTrans = int(np.floor(len(stack_curvaLuz[count4]) / 2))
            min_D = np.min(stack_curvaLuz)
            D_lambda_mid = stack_curvaLuz[count4]
            # Transit depth in ppm
            D_lambda[count4] = (1.0 - D_lambda_mid[index_midTrans]) * 1.e6
            count4 += 1
            count_palette -= 1
        
        pyplot.axis([-tempoTransito/5, tempoTransito/5, min_D, 1.00005])
        pyplot.xlabel("$\\mathbf{Time\\;from\\;transit\\;center\\;(hr)}$", fontsize=19)
        pyplot.ylabel("$\\mathbf{Relative\\;flux}$", fontsize=19)
        pyplot.tick_params(axis="x", direction="in", labelsize=12, length=7, width=2, top=True)
        pyplot.tick_params(axis="y", direction="in", labelsize=12, length=7, width=2, right=True)
        pyplot.rcParams['axes.linewidth'] = 2  # Aumenta a espessura das bordas dos eixos
        pyplot.tight_layout()
        pyplot.show()

        D_lambda = np.array(D_lambda)
        lambdaEff_nm = np.array(lambdaEff_nm)
        epsilon_Rackham = np.array(epsilon_Rackham)

        global BASELINE_WAVE, BASELINE_DLAMDA
        if np.isclose(self.r**2, 0.0, atol=1e-20):
            BASELINE_WAVE = lambdaEff_nm.copy()
            BASELINE_DLAMDA = D_lambda.copy()
            print(">>> Baseline computed and stored in memory.")
            epsilon_ourWork = np.full_like(D_lambda, np.nan)
        else:
            if BASELINE_DLAMDA is not None:
                epsilon_ourWork = D_lambda / BASELINE_DLAMDA
                print(">>> epsilon_ourWork computed using the in-memory baseline.")
            else:
                epsilon_ourWork = np.full_like(D_lambda, np.nan)
                print(">>> No in-memory baseline available. epsilon_ourWork set to NaN.")

        # Armazena 6 colunas:
        # f_spot, tempSpot, wavelength, D_lambda, epsilon_Rackham, epsilon_ourWork
        def salvar_dados_simulacao(f_spot, tempSpot, lambdaEff_nm, D_lambda, epsilonRack, epsilon_ourWork):
            f_spot_array   = np.full(len(lambdaEff_nm), f_spot)
            tempSpot_array = np.full(len(lambdaEff_nm), tempSpot)

            out_file = f"simulation_results_{self.target}.txt"

            file_exists = os.path.exists(out_file)

            with open(out_file, 'a') as file:
                if not file_exists:
                    header = "f_spot,tempSpot,wavelength,D_lambda,epsilon_Rackham,epsilon_ourWork"
                    file.write(header + '\n')

                np.savetxt(
                    file,
                    np.transpose([
                        f_spot_array,
                        tempSpot_array,
                        lambdaEff_nm,
                        D_lambda,
                        epsilonRack,
                        epsilon_ourWork
                    ]),
                    delimiter=','
                )

        # Chama a função para salvar os dados da simulação
        salvar_dados_simulacao(
            filling_factor,
            self.tempSpot,
            lambdaEff_nm,
            D_lambda,
            epsilon_Rackham,
            epsilon_ourWork
        )
