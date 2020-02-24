// const ENV = process.env.ENV = process.env.NODE_ENV = 'development';
// const HOST = process.env.HOST || 'localhost';
// const PORT = process.env.PORT || 8080;

// const METADATA = Object.assign({}, {
//     host: HOST,
//     port: PORT,
//     PUBLIC: process.env.PUBLIC_DEV || HOST + ':' + PORT
// });

// module.exports = {
//     devServer: {
//         open: process.platform === 'darwin',
//         port: METADATA.port,
//         host: METADATA.host,
//         public: METADATA.PUBLIC,
//         https: true,
//         hotOnly: false,
//     },
// }

module.exports = {
    devServer: {
        open: process.platform === 'darwin',
        host: '0.0.0.0',
        port: 8080, // CHANGE YOUR PORT HERE!
        https: true,
        hotOnly: false,
    },
}