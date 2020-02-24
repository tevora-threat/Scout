import axios from "axios";
const url = "https://10.6.6.13/api/geocodes/";


class GeoService {
  static getGeocode(geocodeID) {
    return new Promise(async (resolve, reject) => {
      try {
        const res = await axios.get(`${url}${geocodeID}`);
        const data = res.data;

        resolve(
          data.map(geocode => ({
            ...geocode,
            createdAt: new Date(geocode.createdAt)
          }))
        );
      } catch (err) {
        reject(err);
      }
    });
  }
}

export default GeoService;