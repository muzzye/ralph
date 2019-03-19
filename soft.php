<?php

include_once 'noc_api.php';

$noc = new SOFT_NOC('dadapro', 'Madavveronel2017!');

$noc->json = 1;

$noc->buy('FAKEIPADDR', '1y', 2, 'cpanel-admin@dada.eu', 1, 0);
