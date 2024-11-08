
# Use HippUnfold v1.0.0 docker as base
FROM khanlab/hippunfold:v1.1.0

# Remove hippunfold model not used
RUN rm /opt/hippunfold_cache/trained_model.3d_fullres.Task102_hcp1200_T2w.nnUNetTrainerV2.model_best.tar && \
	rm /opt/hippunfold_cache/trained_model.3d_fullres.Task110_hcp1200_b1000crop.nnUNetTrainerV2.model_best.tar && \
	rm /opt/hippunfold_cache/trained_model.3d_fullres.Task205_hcp1200_b1000_finetuneround2_dhcp_T1w.nnUNetTrainerV2.model_best.tar

# Update OS and install prerequisite
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get --allow-releaseinfo-change update
RUN apt-get install -y python3-pip \
	time \
	csh \
	vim \
	tcsh

# Define working directory
RUN mkdir /app
WORKDIR /app
COPY . /app/

# create cache 
RUN mkdir /.cache
RUN chmod -R 777 /.cache

# Add data folder to docker
RUN mkdir /data

# # # Create aidhs environment
# RUN conda env create -f environment.yml

# install hippunfold_toolbox
RUN cd hippunfold_toolbox/ && conda run -n base /bin/bash -c "pip install -e ."
# or download latest hippunfold toolbox
# RUN  mkdir -p /opt/hippunfold_toolbox \
# && git clone https://github.com/jordandekraker/hippunfold_toolbox.git /opt/hippunfold_toolbox
# RUN cd /opt/hippunfold_toolbox/ && conda run -n base /bin/bash -c "pip install -e ."

# upate conda environment with aidhs package
RUN conda run -n base /bin/bash -c "pip install matplotlib==3.5.1 h5py==3.9.0 potpourri3d==0.0.7 neuroCombat==0.2.12 fpdf==1.7.2 joblib==1.2.0 scikit-learn==1.2.2 numpy==1.22.4 pybids==0.16.4 pytest==8.3.2"

# install aidhs package
RUN cd /app/ && conda run -n base /bin/bash -c "pip install -e ."

# Set permissions for the entrypoint
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/bin/bash","entrypoint.sh"]


