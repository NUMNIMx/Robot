import pandas as pd
import matplotlib.pyplot as plt
data = pd.read_csv('Conect.csv')
mean_r1=data.iloc[0].mean()
mean_r2=data.iloc[1].mean()


plt.bar(['USB','Wifi'],[mean_r2,mean_r1])
plt.axhline(mean_r1, color='blue', linestyle='--', linewidth=1, label=f'Mean Row 1: {mean_r1:.4f}')
plt.axhline(mean_r2, color='orange', linestyle='--', linewidth=1, label=f'Mean Row 2: {mean_r2:.4f}')
plt.ylabel('Mean Value')
plt.title('Mean time start Value comparison Between USB and Wifi')
plt.legend()
plt.show()