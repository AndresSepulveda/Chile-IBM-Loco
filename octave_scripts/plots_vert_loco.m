clear all
close all
pkg load octcdf

nc1=netcdf('./loco_trond.nc','r');

tim1=nc1{'time'}(:,:);
   tim1=tim1-tim1(1);
   tim1=tim1/(24*3600);

zs1=nc1{'z'}(:,:); % Dim1 # particules,  #Dim2 time
close(nc1)
%
% Vertical Migration
%
indx=find(zs1 >9999);
zs1(indx)=NaN;

hist(zs1)
print('-dpng', 'hist_profs.png');


mend=ceil(length(zs1)/25)
j=1; % Trayectoria

printall = 0;

for m=1:mend
	figure(m)
	for i=1:25
		subplot(5,5,i)
		plot(tim1,zs1(j,:))
		title(['Trayectoria ',num2str(j)])
		axis([0 40 -50 0])
		j=j+1;
	end
	if printall = 1
		if m < 10
			print('-dpng', ['test_00',num2str(m),'.png']);
		end
		if (m > 9 && m < 100)
			print('-dpng', ['test_0',num2str(m),'.png']);
		end
		if m > 99
			print('-dpng', ['test_',num2str(m),'.png']);
		end
	end
end

