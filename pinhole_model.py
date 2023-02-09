import mitsuba as mi
import drjit as dr

if __name__ == '__main__':
    #mi.set_variant('scalar_rgb')
    mi.set_variant('llvm_ad_rgb')

class PinholeCameraModel(mi.Sensor):
    """No Distortion is assumed. Only focal length and principal point is modeled.
    Parameter list is expected in the following order: fx, fy, cx, cy
    """

    def __init__(self, props=mi.Properties()):
        super().__init__(props)
        
    def sample_ray(self, time, wavelength_sample, position_sample, aperture_sample, active=True):
        
        wavelengths, wav_weight = self.sample_wavelengths(dr.zeros(mi.SurfaceInteraction3f),
                                                          wavelength_sample, active)
        o = self.world_transform().translation()

        [w,h] = self.film().size()
        cx = w/2
        cy = h/2

        f = w * 50.0/36.0
        d = self.world_transform() @ mi.Vector3f(w*(1-position_sample.x)-cx,
                                                 h*(1-position_sample.y)-cy,
                                                 f)
        
        #Noramlize the direction vector
        dist = dr.norm(d)
        inv_dist = 1.0 / dist
        d *= inv_dist
        
        return mi.Ray3f(o, d, time, wavelengths), wav_weight

    def sample_ray_differential(self, time, wavelength_sample, position_sample, aperture_sample, active=True):
        ray, weight = self.sample_ray(time, wavelength_sample, position_sample, aperture_sample, active)
        return mi.RayDifferential3f(ray), weight

if __name__ == '__main__':
    mi.register_sensor("PinholeCameraModel", lambda props: PinholeCameraModel(props))

    film =  {
            'type': 'hdrfilm',
            'width': 1500,
            'height': 1000,
            'rfilter': { 'type': 'gaussian' },
            'sample_border': True
        }

    sensor = mi.load_dict({
        'type' : 'PinholeCameraModel',
        'film' : film,
        'to_world': mi.ScalarTransform4f.rotate(axis=(1, 0, 0), angle=90),
    })

    scene = mi.load_dict({
        'type': 'scene',
        'sensor': sensor,
        'integrator': {'type':'path'},
        'light': {
            'type':'envmap',
                'filename': 'dikhololo_night_4k.exr',
                'to_world': mi.ScalarTransform4f.rotate(axis=(1, 0, 0), angle=90),
        },
    })

    params = mi.traverse(scene)
    image = mi.render(scene, spp=256)
    mi.util.write_bitmap("renders/pinhole_model.png", image)


