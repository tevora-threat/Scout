import axios from "axios";
const url = "https://10.6.6.13/api/drives/";


class DriveService {
    static getDrives() {
        return new Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(url);
                const data = res.data;

                resolve(
                    data.map(drive => ({
                        ...drive,
                        createdAt: new Date(drive.createdAt)
                    }))
                );
            } catch (err) {
                reject(err);
            }
        });
    }

    static insertDrive(text) {
        return axios.drive(url, {
            text
        });
    }

    static deleteDrive(id) {
        return axios.delete(`${url}${id}`);
    }
}

export default DriveService;