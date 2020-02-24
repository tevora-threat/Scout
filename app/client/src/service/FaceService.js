import axios from 'axios';
const url = 'https://10.6.6.13/api/faces/';

class FaceService {
    static getFaces() {
        return new Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(url);
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



    static insertFace(text) {
        return axios.face(url, {
            text
        })
    }

    static nameFace(name, id) {
        //we now need up update the name not only for the face but also for any faceDetections. also need to set notNamed to false for both/all
        return axios.post(`${url}${id}`, {
                name: name,
                notNamed: false
            })
            .then(function (response) {
                console.log(response);
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    static makeStranger(detectionID, oldFaceID) {
        console.log(`oldFaceID is:${oldFaceID}`);

        //we now need up update the name not only for the face but also for any faceDetections. also need to set notNamed to false for both/all
        return axios.post(`${url}${detectionID}`, {
                makeStranger: true,
                oldFaceID: oldFaceID
            })
            .then(function (response) {
                console.log(response);
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    static updateDetection(detectionID, oldFaceID, newFaceID, newName) {
        //we now need up update the name not only for the face but also for any faceDetections. also need to set notNamed to false for both/all
        return axios.post(`${url}${detectionID}`, {
                updateDetection: true,
                oldFaceID: oldFaceID,
                newFaceID: newFaceID,
                newName: newName
            })
            .then(function (response) {
                console.log(response);
            })
            .catch(function (error) {
                console.log(error);
            });
    }



    static deleteFace(id) {
        return axios.delete(`${url}${id}`)
    }
}

export default FaceService