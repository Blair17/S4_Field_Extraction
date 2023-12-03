pcall(load(S4.arg))

local filespectrum = io.open("field.csv","w")
local fileeps = io.open("eps_r.csv","w")
    
S = S4.NewSimulation()
S:SetLattice(period)
S:SetNumG(nharm)
S:UsePolarizationDecomposition()

S:AddMaterial("GratingMaterial", {gratingindex^2,0})
S:AddMaterial("Air", {coverindex^2,0})
S:AddMaterial("SiO2", {sio2index^2,0})
S:AddMaterial("Alox", {aloxindex^2,0})

S:AddLayer('AirAbove', 0, 'Air')
S:AddLayer('Grating', gratingthickness, 'Air') -- Air inbetween
S:SetLayerPatternRectangle('Grating', 'GratingMaterial', {0,0}, 0, {ridgewidth*0.5,0})
S:AddLayer('Grating1', ITOwg, 'GratingMaterial') 
S:AddLayer('SiDioxide', 0, 'SiO2')

S:SetExcitationPlanewave({0,0},      -- incidence angles (spherical coords: phi [0,180], theta [0,360])
                         {TEamp,0},  -- TE-polarisation amplitude and phase (in degrees)
                         {TMamp,0})  -- TM-polarisation amplitude and phase
    
-- COMPUTE AND SAVE TRANSMISSION / REFLECTION
freq = 1/lambda1
S:SetFrequency(freq)
inc, back = S:GetPowerFlux('AirAbove', 20)
refl = - back/inc

for z = zmin, zmax, zstep do
  lat = ''
  eps = ''

  for x = xmin, xmax, xstep do
    Exr, Eyr, Ezr, Exi, Eyi, Ezi = S:GetEField({x,0,z})

    if TEamp == 1 then
      lat = lat..(Eyr)..','
    else
      lat = lat..(Ezr)..','
    end

    eps_r, eps_i = S:GetEpsilon({x, 0, z})
    eps = eps..eps_r..','            
  end

  lat = string.sub(lat, 1, -2)
  lat = lat..'\n'
  eps = string.sub(eps, 1, -2)
  eps = eps..'\n'

  filespectrum:write(lat) 
  fileeps:write(eps) 
  print('z=', z) 
end 

filespectrum:close()
fileeps:close()

