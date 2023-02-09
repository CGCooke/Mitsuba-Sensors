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
        d = self.world_transform() @ mi.Vector3f(w*(1-position_sample.x)-cx, h*(1-position_sample.y)-cy, f)
        
        #Noramlize the direction vector
        dist = dr.norm(d)
        inv_dist = 1.0 / dist
        d *= inv_dist

        '''
        Vector2f scaled_principal_point_offset =
            m_film->size() * m_principal_point_offset / m_film->crop_size();

        // Compute the sample position on the near plane (local camera space).
        Point3f near_p = m_sample_to_camera *
                         Point3f(position_sample.x() + scaled_principal_point_offset.x(),
                                 position_sample.y() + scaled_principal_point_offset.y(),
                                 0.f);

        // Convert into a normalized ray direction; adjust the ray interval accordingly.
        Vector3f d = dr::normalize(Vector3f(near_p));

        ray.o = m_to_world.value().translation();
        ray.d = m_to_world.value() * d;

        Float inv_z = dr::rcp(d.z());
        Float near_t = m_near_clip * inv_z,
              far_t  = m_far_clip * inv_z;
        ray.o += ray.d * near_t;
        ray.maxt = far_t - near_t;
        '''

        
        return mi.Ray3f(o, d, time, wavelengths), wav_weight

    def sample_ray_differential(self, time, wavelength_sample, position_sample, aperture_sample, active=True):
        ray, weight = self.sample_ray(time, wavelength_sample, position_sample, aperture_sample, active)
        return mi.RayDifferential3f(ray), weight

    '''
    def sample_direction(self, it, sample, active=True):
        # Transform the reference point into the local coordinate system
        trafo = self.world_transform()
        ref_p = trafo.inverse() @ it.p
        d = mi.Vector3f(ref_p)
        dist = dr.norm(d)
        inv_dist = 1.0 / dist
        d *= inv_dist
        resolution = self.film().crop_size()

        ds = dr.zeros(mi.DirectionSample3f)
        

        ds.uv = mi.Point2f(dr.atan2(d.x, -d.z) * dr.inv_two_pi, dr.safe_acos(d.y) * dr.inv_pi)
        ds.uv.x -= dr.floor(ds.uv.x)
        ds.uv *= resolution
        
        sin_theta = dr.safe_sqrt(1 - d.y * d.y)

        ds.p = trafo.translation()
        ds.d = (ds.p - it.p) * inv_dist
        ds.dist = dist
        ds.pdf = dr.select(active, 1.0, 0.0)

        weight = (1 / (2 * dr.pi * dr.pi * dr.maximum(sin_theta, dr.epsilon(mi.Float)))) * dr.sqr(inv_dist)
        return ds, mi.Spectrum(weight)
    '''

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


