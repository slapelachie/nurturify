install_dir = ${HOME}/.local/bin/
name = nurturify

make:
	cd src/; zip -r ../${name}.zip *
	echo "#!/usr/bin/env python" | cat - ${name}.zip > ${name}

install:
	[ -d ${HOME}/.local/share/${name} ] || mkdir -p ${HOME}/.local/share/${name}
	cp assets/scribbles/* ${HOME}/.local/share/${name}/
	install -m 700 ${name} ${install_dir}

clean:
	rm -f ${name}{,.zip}
	