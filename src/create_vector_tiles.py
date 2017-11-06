from gbdx_task_interface.gbdx_task_autoloader import GbdxTaskAutoloader
import os
from subprocess import check_call, CalledProcessError
import json


class TaskError(BaseException):
    pass


class CreateVectorTilesTask(GbdxTaskAutoloader):

    def get_layer_name(self, filepath):
        basename = os.path.splitext(os.path.basename(filepath))[0]
        if basename in self.inputs.layers.value:
            return self.inputs.layers.value[basename]
        else:
            return basename

    def get_geojson_files(self):
        geojson_files = []

        for input_file in os.listdir(self.inputs.data.value):
            basename, ext = os.path.splitext(input_file)
            full_path = os.path.abspath(os.path.join(
                self.inputs.data.value,
                input_file
            ))

            if ext not in ['.json', '.geojson']:
                try:
                    new_file = os.path.abspath(os.path.join(self.inputs.data.value, '{basename}.geojson'.format(
                        basename=basename
                    )))
                    cmd = 'ogr2ogr -f "GeoJSON" {new_file} {input_path} -t_srs EPSG:4326'.format(
                        new_file=new_file,
                        input_path=full_path
                    )
                    check_call(cmd, shell=True)

                    geojson_files.append(new_file)

                except CalledProcessError as e:
                    if not self.inputs.skip_errors.value:
                        raise TaskError('Error converting {input_file} to GeoJSON: \n{error_message}'.format(
                            input_file=input_file,
                            error_message=e.output
                        ))
                    continue
            elif full_path not in geojson_files:
                geojson_files.append(full_path)

        return geojson_files

    def execute_tippecanoe(self, input_files, output_dir):
        # Compose input files arguments
        input_arguments = ' '.join(input_files)

        # Compose the layers arguments
        layers_arguments = []
        for input_file in input_files:
            layer_name = self.get_layer_name(input_file)
            arg_string = '--named-layer={layer_name}:{input_file}'.format(
                layer_name=layer_name,
                input_file=input_file
            )
            layers_arguments.append(arg_string)
        layers_argument = ' '.join(layers_arguments)

        # Compose the output argument
        output_full_path = os.path.abspath(os.path.join(output_dir, self.inputs.name.value))
        output_argument = '-o {output_file}.mbtiles'.format(output_file=output_full_path)

        cmd = 'tippecanoe {output_argument} {layers_argument} -zg {input_arguments}'.format(
            output_argument=output_argument,
            layers_argument=layers_argument,
            input_arguments=input_arguments
        )
        check_call(cmd, shell=True)

    def invoke(self):

        # Ensure the output directory exists
        output_dir = self.get_output_data_port('data')
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        vt_input_files = self.get_geojson_files()

        self.execute_tippecanoe(vt_input_files, output_dir)

        self.status = 'success'
        self.reason = 'Successfully created {output_file}.mbtiles'.format(output_file=self.inputs.name.value)


if __name__ == '__main__':
    with CreateVectorTilesTask() as task:
        task.invoke()
