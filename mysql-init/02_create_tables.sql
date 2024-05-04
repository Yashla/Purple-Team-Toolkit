USE scan;

CREATE TABLE `cves` (
  `cve_id` varchar(64) NOT NULL,
  `summary` text,
  `cvss_v3_score` text,
  `cvss_v3_label` text
);

CREATE TABLE `devices` (
  `id` int NOT NULL,
  `ip_address` varchar(15) NOT NULL,
  `device_type` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
);

CREATE TABLE `devices_information` (
  `id` int NOT NULL,
  `device_id` int DEFAULT NULL,
  `ip_address` varchar(255) NOT NULL,
  `device_type` text NOT NULL,
  `Vendor` varchar(255) NOT NULL,
  `Product` varchar(255) NOT NULL,
  `Version` varchar(255) NOT NULL
);

CREATE TABLE `device_cves` (
  `id` int NOT NULL,
  `device_id` int DEFAULT NULL,
  `cve_id` varchar(64) DEFAULT NULL
);

CREATE TABLE `snmp_outputs` (
  `id` int NOT NULL,
  `filename` varchar(255) NOT NULL,
  `data` blob NOT NULL
);

CREATE TABLE `ssdp_outputs` (
  `id` int NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `output_blob` blob NOT NULL
);

CREATE TABLE `user` (
  `id` int NOT NULL,
    `username` varchar(100) NOT NULL,
      `password_hash` varchar(512) NOT NULL
      );

-- Indexes for table `cves`
--
ALTER TABLE `cves`
  ADD PRIMARY KEY (`cve_id`);

--
-- Indexes for table `devices`
--
ALTER TABLE `devices`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `devices_information`
--
ALTER TABLE `devices_information`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `device_id` (`device_id`);

--
-- Indexes for table `device_cves`
--
ALTER TABLE `device_cves`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cve_id` (`cve_id`),
  ADD KEY `device_id` (`device_id`);

--
-- Indexes for table `snmp_outputs`
--
ALTER TABLE `snmp_outputs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ssdp_outputs`
--
ALTER TABLE `ssdp_outputs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `devices`
--
ALTER TABLE `devices`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `devices_information`
--
ALTER TABLE `devices_information`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `device_cves`
--
ALTER TABLE `device_cves`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=91;

--
-- AUTO_INCREMENT for table `snmp_outputs`
--
ALTER TABLE `snmp_outputs`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `ssdp_outputs`
--
ALTER TABLE `ssdp_outputs`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `devices_information`
--
ALTER TABLE `devices_information`
  ADD CONSTRAINT `devices_information_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);

--
-- Constraints for table `device_cves`
--
ALTER TABLE `device_cves`
  ADD CONSTRAINT `device_cves_ibfk_1` FOREIGN KEY (`cve_id`) REFERENCES `cves` (`cve_id`),
  ADD CONSTRAINT `device_cves_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);
COMMIT;

