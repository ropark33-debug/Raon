def main():
    
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
SURFACE.fill(255, 255, 255)
 

pygame.draw.rect(SURFACE, (255, 0, 0), (10, 20, 100, 50))


pygame.display.rect(SURFACE, (255, 0, 0), (10, 20, 100, 50))

pygame.draw.rect(SURFACE, (255, 0, 0), (100, 80, 80, 50))


pygame.display.update()
    FPSCLOCK.tick(3)
    
 if __name__ == '__main__':
    main()