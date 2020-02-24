import axios from 'axios';
const url = 'https://10.6.6.13/api/plates/';


class PlateService {

    static getDetectionsForPlate(plateID) {
        return new Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(`${url}detections/${plateID}`);
                const data = res.data;
                resolve(data.map(face => ({
                    ...face,
                    createdAt: new Date(face.createdAt)
                })));
            } catch (err) {
                reject(err);
            }
        })
    }



    static getPlates() {
        return new Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(url);
                const data = res.data;
                resolve(data.map(plate => ({
                    ...plate,
                    createdAt: new Date(plate.createdAt)
                })));
            } catch (err) {
                reject(err);
            }
        })
    }

    static getAllPlates() {
        return new Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(url);
                const data = res.data;

                data.forEach(singlePlate => {
                    // console.log(`getAllPlatesData${singlePlate.plateContent}`);

                    // console.log(this.getDetectionsForPlate(singlePlate._id));
                    var plateDetectionData = this.getDetectionsForPlate(singlePlate._id)
                    singlePlate.numDetections = plateDetectionData.length;
                    console.log(plateDetectionData.length);


                });



                resolve(data.map(plate => ({
                    ...plate,
                    createdAt: new Date(plate.createdAt)
                })));
            } catch (err) {
                reject(err);
            }
        })
    }


    static getDetections() {
        return new Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(`${url}detections`);
                const data = res.data;
                resolve(data.map(face => ({
                    ...face,
                    createdAt: new Date(face.createdAt)
                })));
            } catch (err) {
                reject(err);
            }
        })
    }

    static getAllDetectionsDD() {
        return new Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(`${url}alldetectionsdd`);
                const data = res.data;
                resolve(data.map(face => ({
                    ...face,
                    createdAt: new Date(face.createdAt)
                })));
            } catch (err) {
                reject(err);
            }
        })
    }

    static getAllDetections() {
        return new Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(`${url}alldetections`);
                const data = res.data;
                resolve(data.map(face => ({
                    ...face,
                    createdAt: new Date(face.createdAt)
                })));
            } catch (err) {
                reject(err);
            }
        })
    }


    static insertPlate(text) {
        return axios.plate(url, {
            text
        })
    }

    static deletePlate(id) {
        return axios.delete(`${url}${id}`)
    }
}

export default PlateService