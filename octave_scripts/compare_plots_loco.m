clear all
close all
% pkg load octcdf

nc1=netcdf('./results/loco_opendrift_01052008_to_10092008_experiment_2.nc','r');
%%nc2=netcdf('./results/loco_opendrift_01112019_to_20112019_experiment_2.nc','r');
%%nc3=netcdf('./results/loco.nc','r');

tim1=nc1{'time'}(:,:);
   tim1=tim1-tim1(1);
   tim1=tim1/(24*3600);
%%tim2=nc2{'time'}(:,:);
%%   tim2=tim2-tim2(1);
%%   tim2=tim2/(24*3600);
%%tim3=nc3{'time'}(:,:);
%%   tim3=tim3-tim3(1);
%%   tim3=tim3/(24*3600);

zs1=nc1{'z'}(:,:);
zs2=nc2{'z'}(:,:);
%%zs3=nc3{'z'}(:,:);

%
% Vertical Migration
%
subplot(3,1,1)
plot(tim1,zs1(1,:))
title('Mercator Exp 1')
subplot(3,1,2)
plot(tim1,zs1(10,:))
title('Mercator Exp 2')
subplot(3,1,3)
plot(tim1,zs1(1,:))
title('Loco')

