"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const lib_1 = require("gmail-processor/src/lib");
const handler = async (event) => {
    const invoiceFilterRgx = "^(invoice|Invoice|Rechnung|Honorar|Rng|rng)$";
    const defaultConfig = {
        description: "This is a simple example to start with Gmail Processor.",
        settings: {
            markProcessedLabel: "to-datev/processed",
        },
        messages: [
            {
                attachments: [
                    {
                        match: {
                            contentType: ".pdf",
                            name: invoiceFilterRgx,
                        },
                    },
                ],
                match: {
                    plainBody: invoiceFilterRgx,
                },
                actions: [
                    {
                        name: "message.forward",
                        args: {
                            to: "juliandemourgues@gmail.com",
                        },
                        // to: "ai+edurata_gmbh_julian_de_mourgue@belegarchiv.online",
                    },
                ],
            },
        ],
    };
    const result = (0, lib_1.run)(event.config);
    console.log(result);
};
exports.default = handler;
