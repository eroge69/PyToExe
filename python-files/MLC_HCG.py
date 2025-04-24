from pylinac import PicketFence, DRGS, DRMLC
import pylinac
import numpy as np
import datetime
import os
from reportlab.pdfgen import canvas

# --- PICKET-FENCE ESTÁTICO---

pf=PicketFence(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_0-0.dcm")
pf.analyze(tolerance=0.5,action_tolerance=0.25)
print(pf.results())
pf.plot_analyzed_image()
pf.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\PF_0.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_0-0.dcm")

pf=PicketFence(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_90-0.dcm")
pf.analyze(tolerance=0.5,action_tolerance=0.25)
print(pf.results())
pf.plot_analyzed_image()
pf.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\PF_90.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_90-0.dcm")

pf=PicketFence(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_180-0.dcm")
pf.analyze(tolerance=0.5,action_tolerance=0.25)
print(pf.results())
pf.plot_analyzed_image()
pf.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\PF_180.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_180-0.dcm")

pf=PicketFence(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_270-0.dcm")
pf.analyze(tolerance=0.5,action_tolerance=0.25)
print(pf.results())
pf.plot_analyzed_image()
pf.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\PF_270.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_270-0.dcm")

# --- PICKET-FENCE RAPID-ARC---

pf=PicketFence(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_RA-0.dcm")
pf.analyze(tolerance=0.5,action_tolerance=0.25)
print(pf.results())
pf.plot_analyzed_image()
pf.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\PF_RA.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_RA-0.dcm")

# --- PICKET-FENCE RAPID-ARC CON ERRORES---

pf=PicketFence(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_RA_error-0.dcm")
pf.analyze(tolerance=0.5,action_tolerance=0.25)
print(pf.results())
pf.plot_analyzed_image()
pf.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\PF_RA_error.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.PF_RA_error-0.dcm")

# --- DOSE-RATE GANTRY-SPEED ---

drgs=DRGS(image_paths=[r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_open_6X-0.dcm", r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_6X-0.dcm"])
drgs.analyze(tolerance=1.5)
print(drgs.results())
drgs.plot_analyzed_image()
drgs.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\DRGS_6X.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_open_6X-0.dcm")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_6X-0.dcm")

drgs=DRGS(image_paths=[r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_open_6FFF-0.dcm", r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_6FFF-0.dcm"])
drgs.analyze(tolerance=1.5)
print(drgs.results())
drgs.plot_analyzed_image()
drgs.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\DRGS_6FFF.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_open_6FFF-0.dcm")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_6FFF-0.dcm")


drgs=DRGS(image_paths=[r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_open_10X-0.dcm", r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_10X-0.dcm"])
drgs.analyze(tolerance=1.5)
print(drgs.results())
drgs.plot_analyzed_image()
drgs.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\DRGS_10X.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_open_10X-0.dcm")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_10X-0.dcm")


drgs=DRGS(image_paths=[r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_open_10FFF-0.dcm", r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_10FFF-0.dcm"])
drgs.analyze(tolerance=1.5)
print(drgs.results())
drgs.plot_analyzed_image()
drgs.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\DRGS_10FFF.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_open_10FFF-0.dcm")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.DRGS_10FFF-0.dcm")


# --- MLC-SPEED ---

drmlc=DRMLC(image_paths=[r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.MLC_Speed_open-0.dcm", r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.MLC_Speed-0.dcm"])
drmlc.analyze(tolerance=1.5)
print(drmlc.results())
drmlc.plot_analyzed_image()
drmlc.publish_pdf(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\MLC_Speed.pdf")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.MLC_Speed_open-0.dcm")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.MLC_Speed-0.dcm")


# --- DOSIS EN SWEEPING GAP ---

try:
    imagen_g180 = pylinac.image.load(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.Dosimetry_180-0.dcm")
    imagen_g90 = pylinac.image.load(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.Dosimetry_90-0.dcm")
    imagen_g0 = pylinac.image.load(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.Dosimetry_0-0.dcm")
    imagen_g270 = pylinac.image.load(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.Dosimetry_270-0.dcm")
except FileNotFoundError as e:
    print(f"Error: No se encontró el archivo de imagen: {e}")
    exit()

def dosimetry(imagen_g0):

    xmin = int(imagen_g0.center.x - 5)
    xmax = int(imagen_g0.center.x + 5)
    ymin = int(imagen_g0.center.y - 20)
    ymax = int(imagen_g0.center.y + 20)
    
    region= imagen_g0.array[ymin:ymax, xmin:xmax]

    CU_promedio = np.mean(region)
    return CU_promedio

dosimetry_g180 = dosimetry(imagen_g180)
dosimetry_g90 = dosimetry(imagen_g90)
dosimetry_g0 = dosimetry(imagen_g0)
dosimetry_g270 = dosimetry(imagen_g270)

desv_g180 = (dosimetry_g180-dosimetry_g0)*100/dosimetry_g0
desv_g90 = (dosimetry_g90-dosimetry_g0)*100/dosimetry_g0
desv_g0 = (dosimetry_g0-dosimetry_g0)*100/dosimetry_g0
desv_g270 = (dosimetry_g270-dosimetry_g0)*100/dosimetry_g0

print(f"Dosimetry_180º: {dosimetry_g180:.3f} CU, desv= {desv_g180:.2f} %")
print(f"Dosimetry_90º:  {dosimetry_g90:.3f} CU, desv= {desv_g90:.2f} %")
print(f"Dosimetry_0º:   {dosimetry_g0:.3f} CU, desv= {desv_g0:.2f} %")
print(f"Dosimetry_270º: {dosimetry_g270:.3f} CU, desv= {desv_g270:.2f} %")

c = canvas.Canvas(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\Dosimetry_HD.pdf")
c.drawImage(r"Z:\Radiofisica\Cajón de sastre\Fotos Física\Pylinac-GREEN.png",50,750,width=150,height=45)
c.drawString(250,765,"DOSIMETRY HD")
c.drawString(100,650,f"Dosimetry_180º: {dosimetry_g180:.3f} CU, desv= {desv_g180:.2f} %")
c.drawString(100,630,f"Dosimetry_90º:   {dosimetry_g90:.3f} CU, desv= {desv_g90:.2f} %")
c.drawString(100,610,f"Dosimetry_0º:     {dosimetry_g0:.3f} CU, desv= {desv_g0:.2f} %")
c.drawString(100,590,f"Dosimetry_270º: {dosimetry_g270:.3f} CU, desv= {desv_g270:.2f} %")
now=datetime.datetime.now()
c.drawString(50,50,now.strftime("%d-%m-%Y %H:%M"))
c.save()
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.Dosimetry_180-0.dcm")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.Dosimetry_90-0.dcm")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.Dosimetry_0-0.dcm")
os.remove(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT\RI.zzz-IMRT-VMAT.Dosimetry_270-0.dcm")
os.rename(r"Z:\Radiofisica\Planes DICOM\zzz-IMRT-VMAT",r"Z:\Radiofisica\Planes DICOM\MLC")