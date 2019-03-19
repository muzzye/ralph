<?php

include_once 'noc_api.php';

$noc = new SOFT_NOC('dadapro', 'Madavveronel2017!');

$noc->json = 1;

var_dump($noc->licenses());
