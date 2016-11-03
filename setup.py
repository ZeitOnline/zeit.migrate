from setuptools import setup, find_packages


setup(
    name='zeit.migrate',
    version='1.0.0.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="DAV migrations",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'lxml',
        'setuptools',
        'tinydav == 0.7.5+patchmultipleprops3'
    ],
    extras_require={'test': [
        'mock',
        'pytest',
    ]},
    entry_points={
    },
)
