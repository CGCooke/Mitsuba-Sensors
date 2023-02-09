import mitsuba as mi
import drjit as dr

if __name__ == '__main__':
    mi.set_variant('llvm_ad_rgb')

if __name__ == '__main__':
    film =  {
            'type': 'hdrfilm',
            'width': 1500,
            'height': 1000,
            'rfilter': { 'type': 'gaussian' },
            'sample_border': True
        }

    sensor = mi.load_dict({
        'type' : 'perspective',
        'film' : film,
        'focal_length': '50mm',
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
    mi.util.write_bitmap("renders/perspective_model.png", image)


