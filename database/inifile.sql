CREATE TABLE pricePrediction (
    time DATETIME NOT NULL,
    price DECIMAL(8, 2),
    PRIMARY KEY ( time )
);

CREATE TABLE rseMarket (
    settlementDate DATETIME NOT NULL,
    settlementPeriod INT NOT NULL,
    clearoutPrice DECIMAL(8, 2),
    clearoutVolume DECIMAL(8, 2),
    imbalancePrice DECIMAL(8, 2),
    PRIMARY KEY (settlementDate, settlementPeriod)
);

CREATE TABLE elexonB0620 (
    settlementDate DATETIME NOT NULL,
    settlementPeriod INT NOT NULL,
    quantity INT,
    activeFlag VARCHAR(16),
    PRIMARY KEY (settlementDate, settlementPeriod)
);

CREATE TABLE elexonB1620 (
    settlementDate DATETIME NOT NULL,
    settlementPeriod INT NOT NULL,
    biomass INT,
    hydroPumpedStorage INT,
    hydroRunofriverAndPoundage INT,
    fossilHardCoal INT,
    fossilGas INT,
    fossilOil INT,
    nuclear INT,
    windOnshore INT,
    windOffshore INT,
    solar INT,
    other INT,
    PRIMARY KEY (settlementDate, settlementPeriod)
);


CREATE TABLE carbon_dioxide(
    time DATETIME NOT NULL,
    intensity INT,
    indicator VARCHAR(16),
    location VARCHAR(64),
    fuel_gas DECIMAL(8,2),
    fuel_coal DECIMAL(8,2),
    fuel_biomass DECIMAL(8,2),
    fuel_nuclear DECIMAL(8,2),
    fuel_hydro DECIMAL(8,2),
    fuel_imports DECIMAL(8,2),
    fuel_other DECIMAL(8,2),
    fuel_wind DECIMAL(8,2),
    fuel_solar DECIMAL(8,2),
    PRIMARY KEY ( time )
);

CREATE TABLE carbon_dioxide_saved(
    time DATETIME NOT NULL,
    co2saved DECIMAL(8,2),
    PRIMARY KEY ( time )
);