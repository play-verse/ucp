<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">
    <meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport">
    <title><?= $title ?> - HaiLembur</title>
    <!-- Favicon-->
    <!-- <link rel="icon" href="favicon.ico" type="image/x-icon"> -->

    <!-- Bootstrap Core Css -->
    <link href="<?= base_url(); ?>assets/plugins/bootstrap/css/bootstrap.css" rel="stylesheet">

    <!-- Bootstrap Select Css -->
    <link href="<?= base_url(); ?>assets/plugins/bootstrap-select/css/bootstrap-select.css" rel="stylesheet" />

    <!-- Bootstrap Material Datetime Picker Css -->
    <link href="<?= base_url(); ?>assets/plugins/bootstrap-material-datetimepicker/css/bootstrap-material-datetimepicker.css" rel="stylesheet" />

    <!-- Bootstrap DatePicker Css -->
    <link href="<?= base_url(); ?>assets/plugins/bootstrap-datepicker/css/bootstrap-datepicker.css" rel="stylesheet" />

    <!-- Waves Effect Css -->
    <link href="<?= base_url(); ?>assets/plugins/node-waves/waves.css" rel="stylesheet" />

    <!-- Animation Css -->
    <link href="<?= base_url(); ?>assets/plugins/animate-css/animate.css" rel="stylesheet" />

    <!-- Morris Chart Css-->
    <link href="<?= base_url(); ?>assets/plugins/morrisjs/morris.css" rel="stylesheet" />

    <!-- Custom Css -->
    <link href="<?= base_url(); ?>assets/css/style.css" rel="stylesheet">

    <!-- My Css -->
    <link href="<?= base_url(); ?>assets/css/my.css" rel="stylesheet">

    <!-- AdminBSB Themes. You can choose a theme from css/themes instead of get all themes -->
    <link href="<?= base_url(); ?>assets/css/themes/all-themes.css" rel="stylesheet" />
</head>

<body class="theme-red">
    <!-- Page Loader -->
    <div class="page-loader-wrapper">
        <div class="loader">
            <div class="preloader">
                <div class="spinner-layer pl-red">
                    <div class="circle-clipper left">
                        <div class="circle"></div>
                    </div>
                    <div class="circle-clipper right">
                        <div class="circle"></div>
                    </div>
                </div>
            </div>
            <p>Please wait...</p>
        </div>
    </div>
    <!-- #END# Page Loader -->
    <!-- Overlay For Sidebars -->
    <div class="overlay"></div>
    <!-- #END# Overlay For Sidebars -->
    <!-- Top Bar -->
    <nav class="navbar">
        <div class="container-fluid">
            <div class="navbar-header">
                <a href="javascript:void(0);" class="bars">
                </a>
                <a class="navbar-brand" href="<?= base_url('home') ?>">
                    <table>
                        <tr>
                            <td>
                                <i class="material-icons col-white" style="font-size: 30px;">schedule</i>
                            </td>
                            <td width="10px"></td>
                            <td>
                                HaiLembur
                            </td>
                        </tr>
                    </table>
                </a>
            </div>
        </div>
    </nav>
    <!-- #Top Bar -->
    <section>
        <!-- Left Sidebar -->
        <aside id="leftsidebar" class="sidebar">
            <!-- User Info -->
            <div class="user-info">
                <div class="image">
                    <img src="<?= base_url() ?>assets/images/user-placeholder.png" width="48" height="48" alt="User" />
                </div>
                <div class="info-container">
                    <div class="name" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><?= $this->session->userdata('nama') ?></div>
                    <div class="email"><?= $this->session->userdata('nip') ?></div>
                    <div class="btn-group user-helper-dropdown">
                        <i class="material-icons" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">keyboard_arrow_down</i>
                        <ul class="dropdown-menu pull-right">
                            <li><a href="<?= base_url("profile") ?>"><i class="material-icons">person</i>Profile</a></li>
                            <li role="separator" class="divider"></li>
                            <li><a href="<?= base_url() ?>home/logout"><i class="material-icons">input</i>Sign Out</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            <!-- #User Info -->
            <!-- Menu -->
            <div class="menu">
                <ul class="list">
                    <li>
                        <a href="<?= base_url('home') ?>">
                            <i class="material-icons col-red">home</i>
                            <span>Home</span>
                        </a>
                    </li>
                    <?php if ($this->session->userdata('is_admin') == '1') : ?>
                        <li class="header">ADMINISTRATOR MENU</li>
                        <li>
                            <a href="<?= base_url('user') ?>">
                                <i class="material-icons col-green">people</i>
                                <span>Kelola User</span>
                            </a>
                        </li>
                        <li>
                            <a href="<?= base_url('golongan') ?>">
                                <i class="material-icons col-light-blue">donut_large</i>
                                <span>Golongan</span>
                            </a>
                        </li>
                        <li>
                            <a href="<?= base_url('unit_kerja') ?>">
                                <i class="material-icons col-red">supervised_user_circle</i>
                                <span>Unit Kerja</span>
                            </a>
                        </li>
                        <li>
                            <a href="<?= base_url('pangkat') ?>">
                                <i class="material-icons col-orange">account_box</i>
                                <span>Pangkat</span>
                            </a>
                        </li>
                        <li class="header">SURAT DAN LAPORAN</li>
                        <li>
                            <a href="<?= base_url('surat') ?>">
                                <i class="material-icons col-lime">mail</i>
                                <span>Surat Permohonan</span>
                            </a>
                        </li>
                        <li>
                            <a href="<?= base_url('history') ?>">
                                <i class="material-icons">history</i>
                                <span>History Pengajuan Lembur</span>
                            </a>
                        </li>
                    <?php endif; ?>
                    <li class="header">USER MENU</li>
                    <li>
                        <a href="<?= base_url('pengajuan_lembur') ?>">
                            <i class="material-icons col-cyan">event_note</i>
                            <span>Pengajuan Lembur</span>
                        </a>
                    </li>
                    <?php if ($this->fungsi_tambahan->getJabatan($this->session->userdata('id_jabatan')) == 'Kasi' || $this->fungsi_tambahan->getJabatan($this->session->userdata('id_jabatan')) == 'Kaka') : ?>
                        <li>
                            <a href="<?= base_url('permintaan_lembur') ?>">
                                <i class="material-icons col-light-green">event_available</i>
                                <span>Permintaan Lembur</span>
                            </a>
                        </li>
                    <?php endif; ?>
                </ul>
            </div>
            <!-- #Menu -->
            <!-- Footer -->
            <div class="legal">
                <div class="copyright">
                    All right reserved &copy; 2020 &bull; <a href="#">HaiLembur</a>.
                </div>
            </div>
            <!-- #Footer -->
        </aside>
        <!-- #END# Left Sidebar -->
    </section>

    <section class="content">
        <div class="container-fluid">
            <div class="block-header">
                <h2><?= $title ?></h2>
            </div>
            <div class="row clearfix">
                <?php if ($this->session->flashdata('success')) : ?>
                    <div class="alert bg-green alert-dismissible" role="alert">
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                        <?= $this->session->flashdata('success') ?>
                    </div>
                <?php endif;
                if ($this->session->flashdata('danger')) : ?>
                    <div class="alert bg-red alert-dismissible" role="alert">
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                        <?= $this->session->flashdata('danger') ?>
                    </div>

                <?php endif; ?>
            </div>