from pymars import mars_spice as ms
from pymars import mars
from pymars import pdstools
from nose.tools import assert_equals

labels = pdstools.get_labels('data/ESP_022699_0985_RED.LBL')


def test_azimuth():
    img = mars.ImgData('/Users/maye/data/hirise/inca_city_dem/latest_download/ESP_022699_0985_RED_A_01_ORTHO.JP2')
    #mspice = ms.MarsSpicer(pdstools.get_time(labels))
    mspicer = ms.MarsSpicer()
    # mspicer.goto_ls_0()
    mspicer.utc = pdstools.get_time(labels)
    mspicer.set_spoint_by(lat=img.center.lat, lon=img.center.lon)
    p2lon, p2lat = mspicer.point_towards_sun(pixel_res=1)
    p2 = mars.Point(lat=p2lat, lon=p2lon)
    p2.lonlat_to_pixel(img.center.geotrans, img.center.proj)
    assert_equals(round(img.center.calculate_azimuth(p2),2),
                  round(pdstools.get_sub_sol_azi(labels),2))


def test_incidence_angle():
    inc = pdstools.get_incidence(labels)
    mspicer = ms.MarsSpicer()
    mspicer.utc = pdstools.get_time(labels)
    lat = pdstools.get_mean_lat(labels)
    lon = pdstools.get_mean_lon(labels)
    mspicer.set_spoint_by(lat=lat, lon=lon)
    calculated_inc = mspicer.illum_angles.dsolar
    # rounding off all fractions here for this test! improve?
    assert_equals(round(calculated_inc), round(inc))


def test_local_solar_time():
    label_time = pdstools.get_local_solar_time(labels)
    mspicer = ms.MarsSpicer()
    mspicer.utc = pdstools.get_time(labels)
    lat = pdstools.get_mean_lat(labels)
    lon = pdstools.get_mean_lon(labels)
    mspicer.set_spoint_by(lat=lat, lon=lon)
    calculated_soltime = mspicer.fractional_local_time
    assert_equals(round(label_time, 1), round(calculated_soltime, 1))       


####
## some example codes i used for development, not necessarily fully functional
####
def plot_times():
    time1 = tparser.parse(mspicer.local_soltime[4])
    time2 = time1 + dt.timedelta(1) # adding 1 day
    delta = dt.timedelta(minutes = 30)
    times = drange(time1, time2, delta)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for time in times:
        mspicer.time += delta
    ax.plot_date(times, angles)
    fig.autofmt_xdate()
    plt.show()

def test_time_series():
    mspice = MarsSpicer()
    mspice.goto_ls_0()
    mspice.set_spoint_by(lat=-84, lon=0)
    mspice.tilt = 15
    mspice.aspect = 90
    mspice.advance_time_by(24*3600*356)
    utc = mspice.utc
    timestep = 600
    no_of_steps = 2000
    times, to_east = mspice.time_series('F_aspect', timestep, no_of_steps, provide_times='l_s')
    mspice.utc = utc
    flat = mspice.time_series('F_flat', timestep, no_of_steps)
    mspice.utc = utc
    tilted = mspice.time_series('F_tilt', timestep, no_of_steps)
    mspice.utc = utc
    mspice.aspect = 270
    to_west = mspice.time_series('F_aspect', timestep, no_of_steps)
    plt.plot(times, flat, '*-', label='flat')
    plt.plot(times, tilted, '*-', label='tilted')
    plt.plot(times, to_east, '*-', label='to_east')
    plt.plot(times, to_west, '*-', label = 'to_west')
    plt.legend()
    plt.show()

def test_phase():
    mspice = MarsSpicer()
    mspice.utc = '2011-05-24T00:58:08.402'
    mspice.obs = 'MRO'
    mspice.instrument = 'MRO_HIRISE'
    mspice.set_spoint_by('sincpt')
    print("Phase: %f" % np.degrees(spice.vsep(spice.vminus(mspice.srfvec), mspice.sun_direction)))
    print("Inc: %f" % np.degrees(spice.vsep(mspice.spoint, mspice.sun_direction)))
    print("Emis: %f" % np.degrees(spice.vsep(mspice.spoint, spice.vminus(mspice.srfvec))))
